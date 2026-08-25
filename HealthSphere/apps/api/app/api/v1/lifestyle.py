"""Lifestyle: profile, exercise/diet/sleep logs, weekly plan generation."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import NotFoundError
from app.clinical.preventive import calculate_bmi
from app.models import (
    DietLog,
    ExerciseLog,
    LifestyleProfile,
    SleepLog,
    User,
    UserProfile,
)
from app.schemas.schemas import (
    ExerciseLogIn,
    ExerciseLogOut,
    LifestyleProfileIn,
    LifestyleProfileOut,
    SleepLogIn,
    SleepLogOut,
)

router = APIRouter(prefix="/lifestyle", tags=["lifestyle"])


@router.get("", response_model=LifestyleProfileOut)
def get_lifestyle(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(LifestyleProfile).filter(LifestyleProfile.user_id == user.id).first()
    if not row:
        row = LifestyleProfile(user_id=user.id, sleep_goal_hours=8.0)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.put("", response_model=LifestyleProfileOut)
def update_lifestyle(
    payload: LifestyleProfileIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.query(LifestyleProfile).filter(LifestyleProfile.user_id == user.id).first()
    if not row:
        row = LifestyleProfile(user_id=user.id)
        db.add(row)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    audit(request, db, user.id, "LIFESTYLE_UPDATED")
    return row


# ---- Logs ----
@router.post("/exercise", response_model=ExerciseLogOut, status_code=201)
def log_exercise(
    payload: ExerciseLogIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = ExerciseLog(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    audit(request, db, user.id, "EXERCISE_LOGGED", "exercise_log", row.id)
    return row


@router.get("/exercise", response_model=list[ExerciseLogOut])
def list_exercise(
    limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return (
        db.query(ExerciseLog).filter(ExerciseLog.user_id == user.id)
        .order_by(ExerciseLog.performed_on.desc()).limit(limit).all()
    )


@router.post("/sleep", response_model=SleepLogOut, status_code=201)
def log_sleep(
    payload: SleepLogIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = SleepLog(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    audit(request, db, user.id, "SLEEP_LOGGED", "sleep_log", row.id)
    return row


@router.get("/sleep", response_model=list[SleepLogOut])
def list_sleep(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(SleepLog).filter(SleepLog.user_id == user.id)
        .order_by(SleepLog.logged_on.desc()).limit(limit).all()
    )


@router.post("/diet", status_code=201)
def log_diet(
    meal: str,
    meal_type: str | None = None,
    calories: float | None = None,
    logged_on: date | None = None,
    notes: str | None = None,
    request: Request = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from datetime import datetime as dt

    row = DietLog(
        user_id=user.id, meal=meal[:255], meal_type=meal_type,
        calories=calories, logged_on=logged_on or dt.now().date(), notes=notes,
    )
    db.add(row)
    db.commit()
    if request:
        audit(request, db, user.id, "DIET_LOGGED", "diet_log", row.id)
    return {"success": True, "id": row.id}


@router.get("/weekly-plan")
def weekly_plan(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """General wellness exercise plan generated deterministically from profile.

    General wellness guidance — not medical treatment. Users with relevant
    medical concerns should consult a professional before major changes.
    """
    profile_row = (
        db.query(LifestyleProfile).filter(LifestyleProfile.user_id == user.id).first()
    )
    activity = profile_row.activity_level if profile_row else None
    goal = profile_row.goal if profile_row else None
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    # Base minutes scale with activity level (WHO guidance suggests ≥150 min/week moderate activity)
    base_minutes = {
        "sedentary": 15, "light": 20, "moderate": 30, "active": 40, "athlete": 45,
    }.get(activity, 20)

    caution = False
    ctx_reasons = []
    age_related = profile and profile.date_of_birth and (
        (date.today() - profile.date_of_birth).days / 365.25) >= 65
    if age_related:
        caution = True
        ctx_reasons.append("age 65+")

    plan = [
        ("Monday", f"Walking — {base_minutes} min"),
        ("Tuesday", "Mobility & stretching — 10 min"),
        ("Wednesday", f"Walking — {base_minutes + 5} min"),
        ("Thursday", "Rest / light movement"),
        ("Friday", f"Walking — {base_minutes + 5} min"),
        ("Saturday", "Light strength or yoga — 15 min" if base_minutes >= 30 else "Stretching — 10 min"),
        ("Sunday", "Rest / leisure walk"),
    ]
    weekly_total = base_minutes * 3 + 10 + 15 + 15
    return {
        "plan": [{"day": d, "activity": a} for d, a in plan],
        "estimated_weekly_minutes": weekly_total,
        "guideline_note": (
            "General adult guidance commonly references about 150 minutes of moderate "
            "activity per week (WHO 2020). Adjust gradually and at your own pace."
        ),
        "caution_note": (
            "Because your profile indicates potentially relevant factors ("
            + ", ".join(ctx_reasons)
            + "), please consult a healthcare professional before making major changes "
            "to your activity levels."
            if caution
            else None
        ),
        "goal": goal,
    }


@router.get("/nutrition-guidance")
def nutrition_guidance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Deterministic general nutrition guidance based on lifestyle profile.

    General wellness guidance only — not therapeutic diet prescriptions.
    """
    lp = db.query(LifestyleProfile).filter(LifestyleProfile.user_id == user.id).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    bmi = calculate_bmi(profile.height_cm if profile else None, profile.weight_kg if profile else None)
    diet_type = lp.diet_type if lp else None

    notes = [
        "Base meals on vegetables, fruits, whole grains, legumes, nuts, and protein sources you tolerate well.",
        "Limit free sugars to under 10% of daily energy intake and salt to under 5 g per day (WHO general guidance).",
        "Prefer unsaturated oils over saturated fats; avoid industrially produced trans fats.",
        "Stay hydrated with water as your primary drink.",
    ]
    if bmi and bmi >= 25:
        notes.append("A modest, gradual approach to weight change is generally easier to sustain than restrictive diets.")
    if diet_type in ("vegetarian", "vegan"):
        notes.append("With plant-based diets, pay attention to iron, vitamin B12, and complete protein combinations.")
    substitutions = [
        {"instead_of": "white rice/refined grains", "try": "brown rice, millets, quinoa"},
        {"instead_of": "deep-fried snacks", "try": "roasted chana, nuts (unsalted), fruit"},
        {"instead_of": "sugary drinks", "try": "water, lemon water, unsweetened tea"},
    ]
    return {
        "notes": notes,
        "substitutions": substitutions,
        "bmi": bmi,
        "disclaimer": (
            "This is general wellness information, not a therapeutic diet prescription. "
            "For conditions like diabetes or kidney disease, ask your doctor or a "
            "registered dietitian for individualized advice."
        ),
    }
