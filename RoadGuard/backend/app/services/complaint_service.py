"""Complaint creation, numbering and duplicate attachment."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import PotholeStatus, Severity
from app.db.models import Pothole, Report
from app.services.cost_estimator import calculate_repair_area, estimate_cost
from app.services.duplicate_detector import find_duplicate


def next_report_code(db: Session) -> str:
    year = datetime.utcnow().year
    prefix = f"RGA-{year}-"
    count = db.execute(
        select(func.count()).select_from(Report).where(Report.report_code.like(f"{prefix}%"))
    ).scalar_one()
    return f"{prefix}{count + 1:06d}"


def next_pothole_code(db: Session) -> str:
    count = db.execute(select(func.count()).select_from(Pothole)).scalar_one()
    return f"PTH-{count + 1:06d}"


def create_or_attach(
    db: Session,
    user_id: str | None,
    analysis: dict,
    image_path: str | None,
    lat: float | None,
    lon: float | None,
    city: str = "",
    district: str = "",
    state: str = "",
    ward: str = "",
    road: str = "",
) -> dict:
    """Create a pothole (or attach the report to a duplicate) and its report."""
    report = Report(
        report_code=next_report_code(db),
        user_id=user_id,
        image_path=image_path,
        latitude=lat,
        longitude=lon,
        city=city,
        district=district,
        state=state,
        ward=ward,
        road=road,
        detected=analysis.get("detected", False),
        ai_confidence=analysis.get("confidence", 0.0),
        severity=Severity(analysis.get("severity", "LOW")),
        status="SUBMITTED",
    )
    db.add(report)
    db.flush()

    duplicate = find_duplicate(db, lat, lon) if lat is not None and lon is not None else None

    if analysis.get("detected", False):
        if duplicate:
            # Attach report to existing pothole.
            duplicate.report_count += 1
            report.is_duplicate = True
            report.duplicate_of = duplicate.id
            report.pothole_id = duplicate.id
            duplicate.status = (
                PotholeStatus.PENDING_VERIFICATION
                if duplicate.status == PotholeStatus.SUBMITTED
                else duplicate.status
            )
            db.commit()
            return {
                "report": report,
                "duplicate": True,
                "pothole": duplicate,
            }

        # New pothole.
        repair_area = calculate_repair_area(analysis.get("estimated_area", 0.0), db)
        cost = estimate_cost(repair_area, db)
        pothole = Pothole(
            pothole_code=next_pothole_code(db),
            latitude=lat or 0.0,
            longitude=lon or 0.0,
            geometry=(
                f"POINT({lon} {lat})" if lat is not None and lon is not None else None
            ),
            city=city,
            district=district,
            state=state,
            ward=ward,
            road=road,
            severity=Severity(analysis.get("severity", "LOW")),
            severity_score=analysis.get("severity_score", 0.0),
            confidence=analysis.get("confidence", 0.0),
            estimated_area=analysis.get("estimated_area", 0.0),
            repair_area=repair_area,
            estimated_cost=cost["total"],
            status=PotholeStatus.PENDING_VERIFICATION,
            report_count=1,
            source="REPORT",
            before_image=image_path,
        )
        db.add(pothole)
        db.flush()
        report.pothole_id = pothole.id
        db.commit()
        return {
            "report": report,
            "duplicate": False,
            "pothole": pothole,
        }

    db.commit()
    return {"report": report, "duplicate": False, "pothole": None}
