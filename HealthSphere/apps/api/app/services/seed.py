"""Development seed data — clearly fictional, never real medical information."""
import logging

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Condition,
    Doctor,
    EmergencyContact,
    FamilyCondition,
    FamilyMember,
    HealthMetricValue,
    Reminder,
    User,
    UserProfile,
)

logger = logging.getLogger("healthsphere.seed")

DEMO_EMAIL = "demo@healthsphere.example.com"
DEMO_PASSWORD = "Demo1234!"  # development only; change immediately in any shared environment


CONDITION_CATALOG = [
    ("Type 2 Diabetes", "endocrine"), ("Hypertension", "cardiovascular"),
    ("Coronary Artery Disease", "cardiovascular"), ("Asthma", "respiratory"),
    ("Hypothyroidism", "endocrine"), ("Anemia", "hematology"),
    ("Chronic Kidney Disease", "renal"), ("Osteoarthritis", "musculoskeletal"),
    ("Migraine", "neurological"), ("High Cholesterol", "metabolic"),
]


def seed_condition_catalog(db: Session) -> None:
    if db.query(Condition).count() == 0:
        for name, category in CONDITION_CATALOG:
            db.add(Condition(name=name, category=category, source="seed-catalog"))
        db.commit()


def seed_demo_data_if_requested(db: Session) -> None:
    """Create a clearly-labelled demo account when SEED_DEMO=1 (or by default in dev)."""
    import os

    if os.environ.get("SEED_DEMO", "1") != "1":
        return
    seed_condition_catalog(db)
    if db.query(User).filter(User.email == DEMO_EMAIL).first():
        return

    logger.info("Seeding FICTIONAL demo data (%s / %s)", DEMO_EMAIL, DEMO_PASSWORD)
    user = User(email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD),
                full_name="Demo User (fictional)")
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        date_of_birth=__import__("datetime").date(1985, 4, 12),
        sex="female", height_cm=165.0, weight_kg=70.0, blood_group="O+",
        allergies="Penicillin (reported)",
        diet_preferences="vegetarian",
    )
    db.add(profile)

    father = FamilyMember(user_id=user.id, relationship="father",
                          name="R. Sharma (fictional)", living_status="living")
    mother = FamilyMember(user_id=user.id, relationship="mother",
                          name="S. Sharma (fictional)", living_status="living")
    grandfather = FamilyMember(user_id=user.id, relationship="grandfather",
                               name="Paternal Grandfather (fictional)", living_status="deceased")
    db.add_all([father, mother, grandfather])
    db.flush()
    db.add_all([
        FamilyCondition(member_id=father.id, condition_name="Type 2 Diabetes", diagnosis_age=52),
        FamilyCondition(member_id=father.id, condition_name="Hypertension", diagnosis_age=48),
        FamilyCondition(member_id=grandfather.id, condition_name="Coronary Artery Disease", diagnosis_age=60),
    ])

    from datetime import date, datetime, timedelta

    today = datetime.combine(date.today(), datetime.min.time())
    metric_rows = []
    for weeks_ago in range(8, -1, -2):
        when = today - timedelta(weeks=weeks_ago)
        weight = 72.5 - (8 - weeks_ago) * 0.3
        metric_rows.append(HealthMetricValue(user_id=user.id, metric_key="weight",
                                             value=weight, unit="kg", recorded_at=when, source="manual"))
        metric_rows.append(HealthMetricValue(user_id=user.id, metric_key="blood_pressure",
                                             value=128 + (8 - weeks_ago), secondary_value=84,
                                             unit="mmHg", recorded_at=when, source="manual"))
    db.add_all(metric_rows)

    db.add_all([
        Doctor(user_id=user.id, doctor_name="Dr. A. Mehta (fictional)", specialty="General Physician",
               clinic="City Family Practice", phone="+91-90000-00001", is_family_doctor=True),
        Doctor(user_id=user.id, doctor_name="Dr. K. Iyer (fictional)", specialty="Cardiology",
               clinic="Heart Care Clinic", phone="+91-90000-00002"),
    ])
    db.add_all([
        EmergencyContact(user_id=user.id, name="Spouse (fictional)", relationship="family",
                         phone="+91-90000-00010", priority=1),
        EmergencyContact(user_id=user.id, name="Neighbour (fictional)", relationship="neighbour",
                         phone="+91-90000-00011", priority=2),
    ])
    db.add(Reminder(user_id=user.id, type="metric_check", title="Record weekly blood pressure",
                    description="Fictional demo reminder.", due_at=today + timedelta(days=3),
                    recurrence="weekly"))

    db.commit()
    logger.info("Demo seed complete.")
