"""Health metrics: record, list, trend."""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import NotFoundError
from app.models import HealthMetricValue, User
from app.schemas.schemas import MetricValueIn, MetricValueOut
from app.services.timeline import add_event
from app.models import TimelineEventType
from app.services.trends import TrendPoint, analyze_trend

router = APIRouter(prefix="/health-metrics", tags=["health-metrics"])

METRIC_LABELS = {
    "weight": "Weight", "height": "Height", "bmi": "BMI", "blood_pressure": "Blood pressure",
    "heart_rate": "Heart rate", "blood_glucose": "Blood glucose", "hba1c": "HbA1c",
    "cholesterol_total": "Total cholesterol", "cholesterol_ldl": "LDL",
    "cholesterol_hdl": "HDL", "triglycerides": "Triglycerides", "sleep_hours": "Sleep",
    "exercise_minutes": "Exercise minutes", "steps": "Steps",
    "blood_glucose_fasting": "Fasting glucose", "hemoglobin": "Hemoglobin",
    "tsh": "TSH", "creatinine": "Creatinine",
}


@router.post("", response_model=MetricValueOut, status_code=201)
def add_metric(
    payload: MetricValueIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from datetime import datetime

    row = HealthMetricValue(
        user_id=user.id,
        metric_key=payload.metric_key,
        value=payload.value,
        secondary_value=payload.secondary_value,
        unit=payload.unit,
        recorded_at=payload.recorded_at or datetime.now(),
        source="manual",
        notes=payload.notes,
    )
    db.add(row)
    label = METRIC_LABELS.get(payload.metric_key, payload.metric_key)
    add_event(
        db,
        user_id=user.id,
        event_type=TimelineEventType.measurement,
        title=f"{label} recorded: {payload.value}{(' ' + payload.unit) if payload.unit else ''}",
        source="user",
        related_entity_type="metric_value",
        related_entity_id=row.id,
    )
    db.commit()
    db.refresh(row)
    audit(request, db, user.id, "METRIC_ADDED", "health_metric_value", row.id)
    return row


@router.get("", response_model=list[MetricValueOut])
def list_metrics(
    metric_key: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(HealthMetricValue).filter(HealthMetricValue.user_id == user.id)
    if metric_key:
        query = query.filter(HealthMetricValue.metric_key == metric_key)
    return query.order_by(HealthMetricValue.recorded_at.desc()).limit(limit).all()


@router.get("/summary")
def metrics_summary(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """Latest value per tracked metric — powers dashboard cards."""
    rows = (
        db.query(HealthMetricValue)
        .filter(HealthMetricValue.user_id == user.id)
        .order_by(HealthMetricValue.recorded_at.desc())
        .limit(400)
        .all()
    )
    latest: dict[str, HealthMetricValue] = {}
    for row in rows:
        latest.setdefault(row.metric_key, row)
    return {
        "metrics": [
            {
                "metric_key": k,
                "display_name": METRIC_LABELS.get(k, k.replace("_", " ").title()),
                "value": v.value,
                "secondary_value": v.secondary_value,
                "unit": v.unit,
                "recorded_at": v.recorded_at,
                "source": v.source,
            }
            for k, v in sorted(latest.items())
        ]
    }


@router.get("/{metric_key}/trend")
def metric_trend(
    metric_key: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(HealthMetricValue)
        .filter(HealthMetricValue.user_id == user.id, HealthMetricValue.metric_key == metric_key)
        .order_by(HealthMetricValue.recorded_at.asc())
        .all()
    )
    if not rows:
        raise NotFoundError(f"No data recorded for '{metric_key}'")
    trend = analyze_trend([TrendPoint(r.recorded_at, r.value) for r in rows])
    return {
        "metric_key": metric_key,
        "unit": rows[0].unit,
        "points": [
            {"date": str(r.recorded_at.date()), "value": r.value, "source": r.source}
            for r in rows
        ],
        "trend": trend.as_dict(),
    }


@router.delete("/{value_id}", status_code=204)
def delete_metric_value(
    value_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.get(HealthMetricValue, value_id)
    if not row or row.user_id != user.id:
        raise NotFoundError("Measurement not found")
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "METRIC_DELETED", "health_metric_value", value_id)
