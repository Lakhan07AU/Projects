"""Doctor & Specialist section: specialties, symptoms, specialist suggestions.

Safety contract: this is healthcare navigation and decision support only.
Suggestions are discussion topics for a qualified professional — never
diagnoses, referrals, or prescriptions.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import AppError, NotFoundError
from app.models import (
    Reminder,
    SpecialistRecommendation,
    Specialty,
    Symptom,
    User,
    UserSymptom,
)
from app.schemas.schemas import (
    AnalyzeResponse,
    RemindMeIn,
    SpecialtyOut,
    SymptomOut,
    UserSymptomIn,
    UserSymptomOut,
    UserSymptomUpdateIn,
)
from app.services.specialist_engine import _rec_out, analyze_specialist_needs

router = APIRouter(tags=["doctors-specialists"])


# ---------------- Specialties ----------------
@router.get("/specialties", response_model=list[SpecialtyOut])
def list_specialties(db: Session = Depends(get_db)):
    return db.query(Specialty).order_by(Specialty.id).all()


# ---------------- Symptom catalog ----------------
@router.get("/symptoms", response_model=list[SymptomOut])
def list_symptoms(
    q: str | None = Query(None, max_length=128),
    db: Session = Depends(get_db),
):
    query = db.query(Symptom)
    if q:
        query = query.filter(Symptom.name.ilike(f"%{q.strip()}%"))
    return query.order_by(Symptom.category, Symptom.name).limit(200).all()


# ---------------- User-reported symptoms ----------------
@router.get("/user/symptoms", response_model=list[UserSymptomOut])
def my_symptoms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(UserSymptom)
        .filter(UserSymptom.user_id == user.id)
        .order_by(UserSymptom.created_at.desc())
        .all()
    )


@router.post("/user/symptoms", response_model=UserSymptomOut, status_code=201)
def add_symptom(
    payload: UserSymptomIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    name = (payload.symptom_name or "").strip()
    if payload.symptom_id:
        catalog = db.get(Symptom, payload.symptom_id)
        if not catalog:
            raise NotFoundError("Symptom not found in the catalog")
        name = catalog.name
    existing = (
        db.query(UserSymptom)
        .filter(
            UserSymptom.user_id == user.id,
            func.lower(UserSymptom.symptom_name) == name.lower(),
        )
        .first()
    )
    if existing:
        raise AppError("CONFLICT", "That symptom is already recorded", 409)

    row = UserSymptom(
        user_id=user.id,
        symptom_id=payload.symptom_id,
        symptom_name=name,
        duration_text=(payload.duration_text or None),
        severity=payload.severity,
        notes=payload.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError("CONFLICT", "Could not save that symptom", 409)
    audit(request, db, user.id, "SYMPTOM_ADDED", "user_symptom", row.id,
          {"name": name})
    return row


@router.put("/user/symptoms/{symptom_row_id}", response_model=UserSymptomOut)
def update_symptom(
    symptom_row_id: int,
    payload: UserSymptomUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(UserSymptom, symptom_row_id), user.id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.commit()
    audit(request, db, user.id, "SYMPTOM_UPDATED", "user_symptom", row.id,
          {"fields": sorted(data.keys())})
    return row


@router.delete("/user/symptoms/{symptom_row_id}", status_code=204)
def delete_symptom(
    symptom_row_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(UserSymptom, symptom_row_id), user.id)
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "SYMPTOM_DELETED", "user_symptom", symptom_row_id)


# ---------------- Specialist suggestions ----------------
@router.post("/specialist-recommendations/analyze", response_model=AnalyzeResponse)
def analyze(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = analyze_specialist_needs(db, user)
    audit(request, db, user.id, "SPECIALIST_ANALYZED", "user", user.id, {
        "red_flag": result["red_flag"],
        "count": len(result["recommendations"]),
    })
    return result


@router.get("/specialist-recommendations")
def list_recommendations(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    rows = (
        db.query(SpecialistRecommendation)
        .filter(SpecialistRecommendation.user_id == user.id)
        .order_by(SpecialistRecommendation.created_at.desc())
        .limit(50)
        .all()
    )
    return [_rec_out(r) for r in rows]


@router.get("/specialist-recommendations/{rec_id}")
def get_recommendation(
    rec_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(SpecialistRecommendation, rec_id), user.id)
    return _rec_out(row)


# ---------------- Follow-up reminder on a recommendation ----------------
WHEN_DELTAS = {
    "tomorrow": timedelta(days=1),
    "in_3_days": timedelta(days=3),
    "next_week": timedelta(days=7),
}


@router.post("/specialist-recommendations/{rec_id}/remind")
def remind_me(
    rec_id: int,
    payload: RemindMeIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rec = _owned(db.get(SpecialistRecommendation, rec_id), user.id)
    if payload.when == "custom":
        if not payload.custom_at:
            raise AppError("VALIDATION_ERROR",
                           "custom_at is required when when='custom'", 422)
        due_at = payload.custom_at
    else:
        due_at = datetime.now() + WHEN_DELTAS[payload.when]

    source = f"spec-rec:{rec.id}"
    existing = (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user.id,
            Reminder.source == source,
            Reminder.status == "open",
        )
        .first()
    )
    if existing:
        # Never create duplicate reminders for the same recommendation.
        return {"reminder_id": existing.id, "due_at": existing.due_at,
                "duplicate": True}

    reminder = Reminder(
        user_id=user.id,
        type="general",
        title=f"Follow up: discuss {rec.specialty_name} suggestion",
        description=(
            f"Discuss this with a qualified healthcare professional. "
            f"Suggested on {rec.created_at.date().isoformat()} — "
            f"{rec.reason[:300]}"
        ),
        due_at=due_at,
        source=source,
    )
    db.add(reminder)
    db.commit()
    audit(request, db, user.id, "REMINDER_CREATED", "reminder", reminder.id,
          {"source": source})
    return {"reminder_id": reminder.id, "due_at": reminder.due_at,
            "duplicate": False}


def _owned(obj, user_id: int):
    if not obj or obj.user_id != user_id:
        raise NotFoundError("Resource not found")
    return obj
