"""Personal health profile, conditions and medications."""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.clinical.preventive import calculate_age, calculate_bmi
from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import NotFoundError
from app.models import Condition, Medication, User, UserCondition, UserProfile
from app.schemas.schemas import (
    ConditionOut,
    MedicationIn,
    MedicationOut,
    ProfileIn,
    ProfileOut,
    UserConditionIn,
    UserConditionOut,
)

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    out = ProfileOut.model_validate(profile)
    out.age = calculate_age(profile.date_of_birth)
    out.bmi = calculate_bmi(profile.height_cm, profile.weight_kg)
    return out


@router.put("/profile", response_model=ProfileOut)
def update_profile(
    payload: ProfileIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    audit(request, db, user.id, "PROFILE_UPDATED")
    out = ProfileOut.model_validate(profile)
    out.age = calculate_age(profile.date_of_birth)
    out.bmi = calculate_bmi(profile.height_cm, profile.weight_kg)
    return out


# ---- Existing conditions ----
@router.get("/conditions/mine", response_model=list[UserConditionOut])
def my_conditions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(UserCondition).filter(UserCondition.user_id == user.id).order_by(UserCondition.created_at.desc()).all()
    )


@router.post("/conditions/mine", response_model=UserConditionOut, status_code=201)
def add_condition(
    payload: UserConditionIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = UserCondition(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.flush()
    # Link to normalized catalog if it exists (case-insensitive)
    normalized = (
        db.query(Condition).filter(Condition.name.ilike(payload.condition_name)).first()
    )
    if normalized:
        row.condition_id = normalized.id
    else:
        db.add(Condition(name=payload.condition_name, source="user-entered"))
        db.commit()
        db.refresh(row)
        row.condition_id = (
            db.query(Condition).filter(Condition.name.ilike(payload.condition_name)).first()
        ).id
    db.commit()
    from app.services.timeline import add_event
    from app.models import TimelineEventType

    add_event(
        db,
        user_id=user.id,
        event_type=TimelineEventType.condition_added,
        title=f"Condition recorded: {payload.condition_name}",
        source="user",
    )
    db.commit()
    audit(request, db, user.id, "CONDITION_ADDED", "user_condition", row.id)
    return row


@router.delete("/conditions/mine/{condition_row_id}", status_code=204)
def delete_condition(
    condition_row_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.get(UserCondition, condition_row_id)
    if not row or row.user_id != user.id:
        raise NotFoundError("Condition not found")
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "CONDITION_DELETED", "user_condition", condition_row_id)


# ---- Medications (records only; the system never manages prescriptions) ----
@router.get("/medications", response_model=list[MedicationOut])
def list_medications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Medication).filter(Medication.user_id == user.id).all()


@router.post("/medications", response_model=MedicationOut, status_code=201)
def add_medication(
    payload: MedicationIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = Medication(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    audit(request, db, user.id, "MEDICATION_RECORDED", "medication", row.id)
    return row


@router.delete("/medications/{med_id}", status_code=204)
def delete_medication(
    med_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.get(Medication, med_id)
    if not row or row.user_id != user.id:
        raise NotFoundError("Medication record not found")
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "MEDICATION_DELETED", "medication", med_id)


# ---- Condition catalog search ----
@router.get("/conditions/search", response_model=list[ConditionOut])
def search_conditions(q: str = Query(min_length=2, max_length=64), db: Session = Depends(get_db)):
    return db.query(Condition).filter(Condition.name.ilike(f"%{q}%")).limit(10).all()
