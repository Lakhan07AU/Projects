"""Medical reports: secure upload, async processing, analysis, comparison."""
from datetime import datetime

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import AppError, NotFoundError
from app.models import DocumentProcessingJob, MedicalEntity, MedicalReport, ReportStatus, User
from app.schemas.schemas import AnalysisOut, EntityOut, EntityPatchIn, ReportOut
from app.services import documents as doc_service
from app.services import tasks
from app.services.trends import TrendPoint, analyze_trend

router = APIRouter(prefix="/reports", tags=["reports"])

ALLOWED_UPLOAD_MIME = {"application/pdf", "image/jpeg", "image/png"}


@router.post("", response_model=ReportOut, status_code=202)
async def upload_report(
    request: Request,
    file: UploadFile = File(...),
    report_date: datetime | None = None,
    category: str = Query("other"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content = await file.read()
    try:
        real_mime = doc_service.validate_file(content, file.content_type or "", settings.max_upload_size_mb)
    except doc_service.DocumentValidationError as exc:
        raise AppError("INVALID_FILE", str(exc), 400)

    from app.services.storage import get_storage

    storage_key = get_storage().save(content, user.id, file.filename or "report")

    if category not in {
        "cbc", "lipid_profile", "hba1c", "blood_glucose", "thyroid", "liver_function",
        "kidney_function", "ecg", "imaging", "prescription", "doctor_note", "other",
    }:
        category = "other"

    report = MedicalReport(
        user_id=user.id,
        file_name=(file.filename or "report")[:255],
        storage_key=storage_key,
        mime_type=real_mime,
        file_size=len(content),
        category=category,
        report_date=report_date.replace(tzinfo=None) if report_date else None,
        status=ReportStatus.uploaded,
    )
    db.add(report)
    db.flush()
    db.add(DocumentProcessingJob(report_id=report.id, status="queued"))

    from app.models import TimelineEventType
    from app.services.timeline import add_event

    add_event(
        db,
        user_id=user.id,
        event_type=TimelineEventType.report_uploaded,
        title=f"Report uploaded: {(file.filename or 'report')[:80]}",
        description=category.replace("_", " "),
        source="user",
        related_entity_type="report",
        related_entity_id=report.id,
    )
    db.commit()
    db.refresh(report)

    tasks.enqueue_process_report(report.id)
    audit(request, db, user.id, "REPORT_UPLOADED", "medical_report", report.id)
    return report


@router.get("", response_model=list[ReportOut])
def list_reports(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    return (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == user.id)
        .order_by(MedicalReport.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def _owned_report(db: Session, user_id: int, report_id: int) -> MedicalReport:
    report = db.get(MedicalReport, report_id)
    if not report or report.user_id != user_id:
        raise NotFoundError("Report not found")
    return report


@router.get("/compare")
def compare_reports(
    a_id: int = Query(alias="a"),
    b_id: int = Query(alias="b"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compare matching test names between two of the user's reports."""
    ra = _owned_report(db, user.id, a_id)
    rb = _owned_report(db, user.id, b_id)

    def entity_map(report: MedicalReport) -> dict[str, MedicalEntity]:
        rows = db.query(MedicalEntity).filter(MedicalEntity.report_id == report.id).all()
        out: dict[str, MedicalEntity] = {}
        for e in rows:
            key = e.test_name.strip().lower()
            # keep the most recent row per test name
            if key not in out or (e.created_at and e.created_at > (out[key].created_at or e.created_at)):
                out[key] = e
        return out

    map_a, map_b = entity_map(ra), entity_map(rb)
    comparisons = []
    for key in sorted(set(map_a) & set(map_b)):
        ea, eb = map_a[key], map_b[key]
        delta = round(eb.value - ea.value, 4)
        direction = "stable"
        tolerance = max(abs(ea.value) * 0.03, 1e-9)
        if abs(delta) > tolerance:
            direction = "increasing" if delta > 0 else "decreasing"
        comparisons.append({
            "test_name": eb.test_name,
            "unit": eb.unit,
            f"report_a": {"id": ra.id, "date": str(ra.report_date or ra.created_at), "value": ea.value,
                          "reference_low": ea.reference_low, "reference_high": ea.reference_high},
            f"report_b": {"id": rb.id, "date": str(rb.report_date or rb.created_at), "value": eb.value,
                          "reference_low": eb.reference_low, "reference_high": eb.reference_high},
            "delta": delta,
            "trend": ("up" if delta > 0 else "down" if delta < 0 else "flat"),
            "direction": direction,
            "note": "Both values were compared only because the same test appears on both reports.",
        })
    return {"report_a": {"id": ra.id, "date": str(ra.report_date or ra.created_at), "file_name": ra.file_name},
            "report_b": {"id": rb.id, "date": str(rb.report_date or rb.created_at), "file_name": rb.file_name},
            "comparisons": comparisons}


@router.get("/{report_id}", response_model=AnalysisOut)
def get_report_analysis(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = _owned_report(db, user.id, report_id)
    entities = (
        db.query(MedicalEntity)
        .filter(MedicalEntity.report_id == report.id)
        .order_by(MedicalEntity.test_name)
        .all()
    )

    comparison = None
    prev = (
        db.query(MedicalReport)
        .filter(
            MedicalReport.user_id == user.id,
            MedicalReport.id != report.id,
            MedicalReport.category == report.category,
        )
        .order_by(MedicalReport.created_at.desc())
        .first()
    )
    if prev:
        prev_entities = {e.test_name.lower(): e for e in db.query(MedicalEntity).filter(MedicalEntity.report_id == prev.id)}
        changes = []
        for ent in entities:
            old = prev_entities.get(ent.test_name.lower())
            if old:
                delta = round(ent.value - old.value, 4)
                changes.append({
                    "test_name": ent.test_name,
                    "previous": old.value,
                    "current": ent.value,
                    "delta": delta,
                    "direction": "up" if delta > 0 else "down" if delta < 0 else "flat",
                    "abnormal_now": ent.abnormal_flag,
                })
        comparison = {"previous_report_id": prev.id, "changes": changes}

    return AnalysisOut(
        report=ReportOut.model_validate(report),
        entities=[EntityOut.model_validate(e) for e in entities],
        comparison=comparison,
    )


@router.get("/{report_id}/trend/{test_name}")
def report_test_trend(
    report_id: int,
    test_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owned_report(db, user.id, report_id)
    rows = (
        db.query(MedicalEntity, MedicalReport)
        .join(MedicalReport, MedicalEntity.report_id == MedicalReport.id)
        .filter(
            MedicalReport.user_id == user.id,
            MedicalEntity.test_name.ilike(test_name),
        )
        .order_by(MedicalReport.created_at.asc())
        .all()
    )
    points = [
        {"date": str(r.report_date or r.created_at.date()), "value": e.value, "unit": e.unit,
         "report_id": r.id}
        for e, r in rows
    ]
    trend = analyze_trend([TrendPoint(r.created_at, float(e.value)) for e, r in rows])
    return {"test_name": test_name, "points": points, "trend": trend.as_dict()}


@router.patch("/{report_id}/entities/{entity_id}", response_model=EntityOut)
def correct_entity(
    report_id: int,
    entity_id: int,
    payload: EntityPatchIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = _owned_report(db, user.id, report_id)
    entity = db.get(MedicalEntity, entity_id)
    if not entity or entity.report_id != report.id:
        raise NotFoundError("Extracted value not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(entity, field, value)

    # Recompute abnormal flag against the (possibly corrected) reference range.
    entity.abnormal_flag = False
    if entity.reference_low is not None and entity.value < entity.reference_low:
        entity.abnormal_flag = True
    if entity.reference_high is not None and entity.value > entity.reference_high:
        entity.abnormal_flag = True
    entity.confidence = 1.0  # human-verified value

    db.commit()
    audit(request, db, user.id, "EXTRACTED_VALUE_CORRECTED", "medical_entity", entity_id)
    return entity


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = _owned_report(db, user.id, report_id)
    from app.services.storage import get_storage

    content = get_storage().read(report.storage_key)
    media = report.mime_type or "application/octet-stream"
    return Response(content=content, media_type=media,
                    headers={"Content-Disposition": f'inline; filename="{report.file_name}"'})


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = _owned_report(db, user.id, report_id)
    from app.services.storage import get_storage

    try:
        get_storage().delete(report.storage_key)
    except Exception:
        pass  # object may already be gone; DB record is authoritative
    db.delete(report)
    db.commit()
    audit(request, db, user.id, "REPORT_DELETED", "medical_report", report_id)


@router.post("/{report_id}/reprocess", response_model=ReportOut)
def reprocess_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retry processing after failure (e.g., AI was temporarily unavailable)."""
    report = _owned_report(db, user.id, report_id)
    report.status = ReportStatus.uploaded
    report.error_message = None
    db.commit()
    tasks.enqueue_process_report(report.id)
    audit(request, db, user.id, "REPORT_REPROCESS_QUEUED", "medical_report", report_id)
    return report
