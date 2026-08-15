"""AI endpoints: repair report generation and government assistant."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.genai.assistant import answer_question
from app.ai.genai.report_generator import generate_repair_report
from app.api.deps import get_current_user, require_government
from app.core.enums import PotholeStatus, Role
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Pothole, User
from app.schemas.ai import AssistantRequest, ReportRequest
from app.services.priority import compute_priority, pending_days_since
from app.services.road_health import health_label
from app.utils.errors import not_found

settings = get_settings()
router = APIRouter(prefix="/api/ai", tags=["ai"])


def _pothole_report_data(p: Pothole) -> dict:
    result = compute_priority(
        severity_score=p.severity_score,
        supporting_reports=p.report_count,
        pending_days=pending_days_since(p.created_at),
    )
    return {
        "id": p.id,
        "pothole_code": p.pothole_code,
        "road": p.road,
        "ward": p.ward,
        "city": p.city,
        "district": p.district,
        "state": p.state,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "confidence": p.confidence,
        "severity": p.severity.value,
        "severity_score": p.severity_score,
        "severity_note": "Estimated severity for triage; engineering assessment required.",
        "estimated_area": p.estimated_area,
        "repair_area": p.repair_area,
        "estimated_cost": p.estimated_cost,
        "priority": p.priority.value,
        "priority_score": p.priority_score,
        "status": p.status.value,
        "report_count": p.report_count,
        "road_health_score": p.road_health,
        "road_health_label": health_label(p.road_health) if p.road_health is not None else "-",
        "ai_mode": "demo" if settings.DEMO_MODE else "real-model",
        "recommended_action": (
            "Critical: schedule immediate repair." if p.severity.value == "CRITICAL"
            else "Schedule repair according to priority queue."
        ),
    }


@router.post("/report")
def generate_report(
    payload: ReportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pothole = db.query(Pothole).filter(Pothole.id == payload.pothole_id).first()
    if not pothole:
        raise not_found("Pothole not found")
    data = _pothole_report_data(pothole)
    return generate_repair_report(data)


@router.post("/assistant")
def assistant(
    payload: AssistantRequest,
    user: User = Depends(require_government),
    db: Session = Depends(get_db),
):
    return answer_question(db, payload.question)
