"""Report endpoints: image analysis and complaint submission."""
from __future__ import annotations

import io
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.ai.cv.area_estimator import AreaEstimator
from app.ai.cv.detector import Detector
from app.ai.cv.segmenter import Segmenter
from app.ai.cv.severity import score_from_detection
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import AIAnalysis, Detection, Report, User
from app.schemas.report import (
    AnalyzeResponse,
    ReportCreate,
    ReportOut,
    ReportSubmitResponse,
)
from app.services.complaint_service import create_or_attach
from app.services.cost_estimator import calculate_repair_area, estimate_cost
from app.utils.errors import bad_request, not_found
from app.utils.file_validation import validate_image

settings = get_settings()
router = APIRouter(prefix="/api/reports", tags=["reports"])

detector = Detector()
segmenter = Segmenter(demo=settings.DEMO_MODE)
area_estimator = AreaEstimator()


def _save_image(content: bytes, folder: str) -> str:
    sub = settings.storage_path / folder
    sub.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}.jpg"
    path = sub / name
    path.write_bytes(content)
    return f"/uploads/{folder}/{name}"


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate, run the CV pipeline and return a complaint preview."""
    content = validate_image(file)
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:  # noqa: BLE001
        raise bad_request("Could not open image") from None
    size = img.size

    detection = detector.detect(content, size)
    demo = detection.get("demo", True)
    if not detection["detected"]:
        # No pothole found: return a clean preview without creating anything.
        return AnalyzeResponse(
            demo_mode=demo,
            detected=False,
            confidence=0.0,
            detections=[],
            severity="LOW",
            severity_score=0.0,
            estimated_area=0.0,
            repair_area=0.0,
            estimated_cost=0.0,
            repair_cost_breakdown={},
            mask_available=False,
            pixel_area=0.0,
            message="No pothole detected in this image. Try a clearer, closer photo.",
        )

    segments = segmenter.segment(img, detection["detections"])
    detections_out = []
    total_pixels = 0.0
    for det, seg in zip(detection["detections"], segments):
        detections_out.append(
            {
                "class_name": det["class"],
                "confidence": det["confidence"],
                "bbox": det["bbox"],
                "area_pixels": seg["pixel_area"],
            }
        )
        total_pixels += seg["pixel_area"]

    conf = max(d["confidence"] for d in detection["detections"])
    sev = score_from_detection(total_pixels, size[0] * size[1], conf)
    area = area_estimator.estimate(total_pixels, conf)
    repair_area = calculate_repair_area(area["estimated_area_m2"], db)
    cost = estimate_cost(repair_area, db)

    image_path = _save_image(content, "potholes")

    report = Report(
        report_code=f"TMP-{uuid.uuid4().hex[:8]}",
        user_id=user.id,
        image_path=image_path,
        detected=True,
        ai_confidence=conf,
        severity=sev["severity"],
        status="SUBMITTED",
    )
    db.add(report)
    db.flush()

    analysis = AIAnalysis(
        report_id=report.id,
        model_name=detection.get("model_name", "demo"),
        model_version=detection.get("model_version", "demo-v1"),
        demo_mode=demo,
        detected=True,
        confidence=conf,
        severity=sev["severity"],
        severity_score=sev["score"],
        estimated_area=area["estimated_area_m2"],
        repair_area=repair_area,
        raw=json.dumps({
            "detections": detections_out,
            "severity": sev,
            "area": area,
            "cost": cost,
        }),
    )
    db.add(analysis)
    db.flush()

    for det in detections_out:
        db.add(Detection(
            report_id=report.id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            bbox=det["bbox"],
            area_pixels=det["area_pixels"],
        ))
    db.commit()

    return AnalyzeResponse(
        demo_mode=demo,
        detected=True,
        confidence=conf,
        detections=detections_out,
        severity=sev["severity"],
        severity_score=sev["score"],
        estimated_area=area["estimated_area_m2"],
        repair_area=repair_area,
        estimated_cost=cost["total"],
        repair_cost_breakdown=cost,
        mask_available=any(s["mask_available"] for s in segments),
        pixel_area=total_pixels,
        message="Demo AI Analysis" if demo else "AI Analysis",
    )


@router.post("", response_model=ReportSubmitResponse, status_code=201)
def submit_report(
    payload: ReportCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create the complaint/pothole from the previewed analysis."""
    if payload.report_id:
        report = db.query(Report).filter(Report.id == payload.report_id).first()
    else:
        # Fallback: the most recent analyzed report by this user.
        report = (
            db.query(Report)
            .filter(Report.user_id == user.id)
            .order_by(Report.created_at.desc())
            .first()
        )
    if not report or not report.detected:
        raise bad_request("Analyze an image first")
    if report.user_id != user.id and user.role.value not in ("GOVERNMENT_OFFICIAL", "ADMIN"):
        raise not_found("Report not found")

    analysis = (
        db.query(AIAnalysis).filter(AIAnalysis.report_id == report.id).first()
    )
    if not analysis:
        raise bad_request("Analysis not found")

    analysis_data = {
        "detected": analysis.detected,
        "confidence": analysis.confidence,
        "severity": analysis.severity,
        "severity_score": analysis.severity_score,
        "estimated_area": analysis.estimated_area,
        "repair_area": analysis.repair_area,
    }

    result = create_or_attach(
        db,
        user_id=user.id,
        analysis=analysis_data,
        image_path=report.image_path,
        lat=payload.latitude,
        lon=payload.longitude,
        city=payload.city,
        district=payload.district,
        state=payload.state,
        ward=payload.ward,
        road=payload.road,
    )
    new_report = result["report"]
    pothole = result["pothole"]

    pothole_data = None
    if pothole:
        pothole_data = {
            "id": pothole.id,
            "pothole_code": pothole.pothole_code,
            "latitude": pothole.latitude,
            "longitude": pothole.longitude,
            "ward": pothole.ward,
            "road": pothole.road,
            "severity": pothole.severity.value,
            "severity_score": pothole.severity_score,
            "estimated_area": pothole.estimated_area,
            "repair_area": pothole.repair_area,
            "estimated_cost": pothole.estimated_cost,
            "priority": pothole.priority.value,
            "status": pothole.status.value,
            "report_count": pothole.report_count,
        }

    return ReportSubmitResponse(
        report=ReportOut.model_validate(new_report),
        duplicate=result["duplicate"],
        pothole=pothole_data,
    )


@router.get("", response_model=list[ReportOut])
def my_reports(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reports = (
        db.query(Report)
        .filter(Report.user_id == user.id)
        .order_by(Report.created_at.desc())
        .all()
    )
    return reports


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: str, user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise not_found("Report not found")
    if report.user_id != user.id and user.role.value not in ("GOVERNMENT_OFFICIAL", "ADMIN"):
        raise not_found("Report not found")
    return report
