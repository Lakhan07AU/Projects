"""Timeline, recommendations and AI insight endpoints."""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import NotFoundError
from app.clinical.preventive import build_health_context, recommend_specialties, run_preventive_engine
from app.models import (
    ClinicalSource,
    HealthTimelineEvent,
    Recommendation,
    TimelineEventType,
    User,
)
from app.schemas.schemas import RecommendationOut, TimelineEventOut

router = APIRouter(tags=["intelligence"])


@router.get("/timeline", response_model=list[TimelineEventOut])
def get_timeline(
    event_type: str | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(HealthTimelineEvent).filter(HealthTimelineEvent.user_id == user.id)
    if event_type:
        try:
            query = query.filter(HealthTimelineEvent.event_type == TimelineEventType(event_type))
        except ValueError:
            raise NotFoundError(f"Unknown event type '{event_type}'")
    return query.order_by(HealthTimelineEvent.event_date.desc()).offset(offset).limit(limit).all()


@router.get("/recommendations", response_model=list[RecommendationOut])
def list_recommendations(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user.id, Recommendation.dismissed.is_(False))
        .order_by(Recommendation.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/recommendations/refresh", status_code=202)
def refresh_recommendations(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Re-run the preventive-care engine against the latest health context."""
    ctx = build_health_context(db, user)
    created = run_preventive_engine(db, user, ctx)
    audit(request, db, user.id, "RECOMMENDATIONS_REFRESHED", metadata={"created": len(created)})
    return {"success": True, "new_recommendations": len(created)}


@router.delete("/recommendations/{reco_id}", status_code=204)
def dismiss_recommendation(
    reco_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reco = db.get(Recommendation, reco_id)
    if not reco or reco.user_id != user.id:
        raise NotFoundError("Recommendation not found")
    reco.dismissed = True
    db.commit()
    audit(request, db, user.id, "RECOMMENDATION_DISMISSED", "recommendation", reco_id)


@router.get("/insights/context")
def intelligence_context(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """The authorized health context used by rules and the AI assistant."""
    ctx = build_health_context(db, user)
    return {
        "age": ctx["age"],
        "sex": ctx["sex"],
        "bmi": ctx["bmi"],
        "family_history": ctx["family_condition_keywords"],
        "flagged_tests": ctx["flagged_test_keywords"],
        "latest_blood_pressure_systolic": ctx["latest_blood_pressure_systolic"],
        "latest_hba1c": ctx["latest_hba1c"],
        "latest_weight_kg": ctx["latest_weight_kg"],
    }


@router.get("/insights/specialists")
def specialist_suggestions(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    ctx = build_health_context(db, user)
    return {"suggestions": recommend_specialties(ctx),
            "note": "These are discussion suggestions only — not referrals or diagnoses."}


@router.get("/sources")
def clinical_sources(db: Session = Depends(get_db)):
    """Transparency: the knowledge sources behind generated guidance."""
    return db.query(ClinicalSource).all()
