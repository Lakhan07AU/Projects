"""Health context builder + preventive-care engine.

Builds the user's authorized HealthContext (facts used by rules and the AI
assistant) using least-necessary data, then runs the deterministic rule engine
to produce discussion-oriented recommendations.
"""
import logging
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.clinical.rules import evaluate_rules
from app.models import (
    FamilyCondition,
    HealthMetricValue,
    MedicalEntity,
    MedicalReport,
    ReportStatus,
    Recommendation,
    RecommendationKind,
    Priority,
    TimelineEventType,
    User,
    UserProfile,
)
from app.services import timeline as timeline_service

logger = logging.getLogger("healthsphere.prevention")


def calculate_age(dob: date | None) -> int | None:
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, today.day))


def calculate_bmi(height_cm: float | None, weight_kg: float | None) -> float | None:
    if not height_cm or not weight_kg or height_cm <= 0:
        return None
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def build_health_context(db: Session, user: User) -> dict:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    from app.models import FamilyMember, UserCondition

    rows = (
        db.query(FamilyCondition.condition_name)
        .join(FamilyMember, FamilyCondition.member_id == FamilyMember.id)
        .filter(FamilyMember.user_id == user.id)
        .all()
    )
    family_conditions = [name.lower() for (name,) in rows]

    own_rows = (
        db.query(UserCondition.condition_name)
        .filter(UserCondition.user_id == user.id)
        .all()
    )
    own_conditions = [name.lower() for (name,) in own_rows]

    latest_report = (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == user.id, MedicalReport.status == ReportStatus.complete)
        .order_by(MedicalReport.created_at.desc())
        .first()
    )
    flagged_tests: list[str] = []
    if latest_report:
        flagged = (
            db.query(MedicalEntity.test_name)
            .filter(MedicalEntity.report_id == latest_report.id, MedicalEntity.abnormal_flag.is_(True))
            .all()
        )
        flagged_tests = [t.lower() for (t,) in flagged]

    def latest_metric(key: str) -> float | None:
        row = (
            db.query(HealthMetricValue.value)
            .filter(HealthMetricValue.user_id == user.id, HealthMetricValue.metric_key == key)
            .order_by(HealthMetricValue.recorded_at.desc())
            .first()
        )
        return float(row[0]) if row else None

    bp = (
        db.query(HealthMetricValue.value)
        .filter(HealthMetricValue.user_id == user.id, HealthMetricValue.metric_key == "blood_pressure")
        .order_by(HealthMetricValue.recorded_at.desc())
        .first()
    )

    bmi = calculate_bmi(profile.height_cm if profile else None, profile.weight_kg if profile else None)

    return {
        "age": calculate_age(profile.date_of_birth if profile else None),
        "sex": profile.sex if profile else None,
        "bmi": bmi,
        "family_condition_keywords": sorted(set(family_conditions)),
        "user_conditions": sorted(set(own_conditions)),
        "flagged_test_keywords": sorted(set(flagged_tests)),
        "latest_blood_pressure_systolic": float(bp[0]) if bp else None,
        "latest_hba1c": latest_metric("hba1c"),
        "latest_weight_kg": latest_metric("weight"),
    }


def run_preventive_engine(db: Session, user: User, ctx: dict | None = None) -> list[Recommendation]:
    from app.models import ClinicalRule

    ctx = ctx or build_health_context(db, user)
    rules = db.query(ClinicalRule).filter(ClinicalRule.enabled.is_(True)).all()
    fired = evaluate_rules(rules, ctx)

    created: list[Recommendation] = []
    for rule in fired:
        exists = (
            db.query(Recommendation)
            .filter(
                Recommendation.user_id == user.id,
                Recommendation.topic == rule.condition,
                Recommendation.source_key == rule.source_key,
                Recommendation.dismissed.is_(False),
            )
            .first()
        )
        if exists:
            continue
        reco = Recommendation(
            user_id=user.id,
            kind=RecommendationKind.preventive_care,
            topic=rule.condition,
            reason=(ctx.get("explanation_note") or rule.explanation or "")[:500],
            guidance=rule.recommendation,
            source_key=rule.source_key,
            priority=Priority(rule.priority.value if hasattr(rule.priority, "value") else rule.priority),
            confidence=0.8,
            payload={"rule_key": rule.rule_key},
        )
        db.add(reco)
        created.append(reco)
        timeline_service.add_event(
            db,
            user_id=user.id,
            event_type=TimelineEventType.recommendation,
            title=f"New guidance topic: {rule.condition.replace('_', ' ')}",
            description="Generated from a validated clinical guideline rule.",
            source=f"rule:{rule.rule_key}",
        )
        if reco.priority == Priority.high:
            # Guidance chain: high-priority signal -> follow-up reminder -> notification.
            # Created only with the recommendation itself, so re-refresh never duplicates.
            from app.models import Reminder
            from app.services.notifications import notify

            topic = rule.condition.replace("_", " ")
            db.add(Reminder(
                user_id=user.id,
                type="metric_check",
                title=f"Follow up: {topic}",
                description=(rule.recommendation or "")[:255],
                due_at=datetime.now() + timedelta(days=14),
                source=f"system:{rule.rule_key}",
            ))
            notify(db, user, f"New health guidance: {topic}",
                   (rule.recommendation or "")[:500])
    db.commit()
    return created


SPECIALTY_MAP = {
    "blood_sugar_context": ("Endocrinology", 0.7),
    "cardiovascular_health": ("Cardiology", 0.74),
    "cholesterol_context": ("Cardiology", 0.68),
    "thyroid_context": ("Endocrinology", 0.7),
    "blood_health": ("Internal Medicine", 0.65),
    "bone_health": ("General Physician", 0.6),
}


def recommend_specialties(ctx: dict) -> list[dict]:
    """Cautious specialty suggestions based on fired risk areas, recorded
    conditions, family history — never a diagnosis or referral."""
    entries: dict[str, dict] = {}

    def add(area: str, specialty: str, confidence: float, basis: str) -> None:
        entry = entries.setdefault(
            area, {"risk_area": area, "specialty": specialty, "confidence": confidence, "basis": []}
        )
        if basis not in entry["basis"]:
            entry["basis"].append(basis)

    for kw in ctx.get("flagged_test_keywords", []):
        if any(k in kw for k in ["glucose", "hba1c"]):
            add("blood_sugar_context", "Endocrinology", 0.7, f"a flagged result ({kw})")
        if any(k in kw for k in ["cholesterol", "ldl", "hdl", "triglyceride"]):
            add("cholesterol_context", "Cardiology", 0.68, f"a flagged result ({kw})")
        if "tsh" in kw or "thyroid" in kw:
            add("thyroid_context", "Endocrinology", 0.7, f"a flagged result ({kw})")
        if "hemoglobin" in kw:
            add("blood_health", "Internal Medicine", 0.65, f"a flagged result ({kw})")
        if "vitamin d" in kw:
            add("bone_health", "General Physician", 0.6, f"a flagged result ({kw})")

    bp_sys = ctx.get("latest_blood_pressure_systolic")
    if bp_sys and bp_sys >= 140:
        add("cardiovascular_health", "Cardiology", 0.74,
            f"a recorded blood pressure of {bp_sys:g}")

    # Keep specialty suggestions consistent with the rule engine: a raised
    # HbA1c (even from manual entries, not just flagged report entities)
    # is worth a blood-sugar discussion.
    hba1c = ctx.get("latest_hba1c")
    if hba1c and hba1c >= 5.7:
        add("blood_sugar_context", "Endocrinology", 0.72,
            f"an HbA1c of {hba1c:g}%")

    for kw in ctx.get("user_conditions", []):
        for frag, (specialty, area) in CONDITION_SPECIALTY_MAP.items():
            if frag in kw:
                add(area, specialty, 0.75, f"your recorded condition \u201c{kw}\u201d")

    for kw in ctx.get("family_condition_keywords", []):
        for frag, (specialty, area) in CONDITION_SPECIALTY_MAP.items():
            if frag in kw:
                add(area, specialty, 0.55, f"your family history ({kw})")

    results = []
    for entry in entries.values():
        basis = "; ".join(entry["basis"])
        results.append({
            "risk_area": entry["risk_area"],
            "specialty": entry["specialty"],
            "confidence": entry["confidence"],
            "reason": (
                f"Some of your records relate to {entry['risk_area'].replace('_', ' ')} — "
                f"{basis}. A {entry['specialty']} consultation may be worth discussing "
                f"with your primary-care physician."
            ),
        })
    results.sort(key=lambda r: -r["confidence"])
    return results


CONDITION_SPECIALTY_MAP = {
    # fragment -> (specialty, risk area)
    "diabet": ("Endocrinology", "blood_sugar_context"),
    "thyroid": ("Endocrinology", "thyroid_context"),
    "pcos": ("Endocrinology", "hormonal_health"),
    "pcod": ("Endocrinology", "hormonal_health"),
    "obesity": ("Endocrinology", "metabolic_health"),
    "hypertens": ("Cardiology", "cardiovascular_health"),
    "blood pressure": ("Cardiology", "cardiovascular_health"),
    "cholesterol": ("Cardiology", "cholesterol_context"),
    "heart diseas": ("Cardiology", "cardiovascular_health"),
    "coronary": ("Cardiology", "cardiovascular_health"),
    "asthma": ("Pulmonology", "breathing_context"),
    "copd": ("Pulmonology", "breathing_context"),
    "arthritis": ("Orthopedics", "bone_health"),
    "osteoporos": ("Orthopedics", "bone_health"),
    "anemia": ("Internal Medicine", "blood_health"),
    "anaemia": ("Internal Medicine", "blood_health"),
    "kidney": ("Nephrology", "kidney_context"),
    "liver": ("Gastroenterology", "digestion_context"),
    "migraine": ("Neurology", "neurological_context"),
    "epilep": ("Neurology", "neurological_context"),
}

SYMPTOM_SPECIALTY_MAP = {
    # fragment -> (specialty, risk area)
    "chest pain": ("Cardiology", "cardiovascular_health"),
    "chest tight": ("Cardiology", "cardiovascular_health"),
    "palpitation": ("Cardiology", "cardiovascular_health"),
    "irregular heartbeat": ("Cardiology", "cardiovascular_health"),
    "swelling in the legs": ("Cardiology", "cardiovascular_health"),
    "shortness of breath": ("Pulmonology", "breathing_context"),
    "breathless": ("Pulmonology", "breathing_context"),
    "wheez": ("Pulmonology", "breathing_context"),
    "chronic cough": ("Pulmonology", "breathing_context"),
    "excessive thirst": ("Endocrinology", "blood_sugar_context"),
    "frequent urination": ("Endocrinology", "blood_sugar_context"),
    "blurred vision": ("Endocrinology", "blood_sugar_context"),
    "heat intolerance": ("Endocrinology", "thyroid_context"),
    "unexplained weight change": ("Endocrinology", "metabolic_health"),
    "joint pain": ("Orthopedics", "bone_health"),
    "joint stiff": ("Orthopedics", "bone_health"),
    "back pain": ("Orthopedics", "bone_health"),
    "swollen joint": ("Orthopedics", "bone_health"),
    "difficulty moving": ("Orthopedics", "bone_health"),
    "rash": ("Dermatology", "skin_context"),
    "itching": ("Dermatology", "skin_context"),
    "eczema": ("Dermatology", "skin_context"),
    "acne": ("Dermatology", "skin_context"),
    "hair loss": ("Dermatology", "skin_context"),
    "persistent headache": ("Neurology", "neurological_context"),
    "migraine": ("Neurology", "neurological_context"),
    "numbness": ("Neurology", "neurological_context"),
    "tingling": ("Neurology", "neurological_context"),
    "dizzin": ("Neurology", "neurological_context"),
    "tremor": ("Neurology", "neurological_context"),
    "anxiety": ("Psychiatry", "mental_health_context"),
    "depress": ("Psychiatry", "mental_health_context"),
    "panic attack": ("Psychiatry", "mental_health_context"),
    "insomnia": ("Psychiatry", "mental_health_context"),
    "low mood": ("Psychiatry", "mental_health_context"),
    "stomach pain": ("Gastroenterology", "digestion_context"),
    "acidity": ("Gastroenterology", "digestion_context"),
    "acid reflux": ("Gastroenterology", "digestion_context"),
    "bloating": ("Gastroenterology", "digestion_context"),
    "constipation": ("Gastroenterology", "digestion_context"),
    "diarrhea": ("Gastroenterology", "digestion_context"),
    "persistent fatigue": ("Internal Medicine", "general_health"),
    "persistent fever": ("Internal Medicine", "general_health"),
    "unexplained weight loss": ("Internal Medicine", "general_health"),
}


def suggest_specialists_for_symptoms(text: str) -> list[dict]:
    """Educational mapping from described symptoms to the specialty that
    typically evaluates them. Never a diagnosis; emergencies are flagged."""
    q = f" {text.lower().strip()} "
    entries: dict[str, dict] = {}
    for kw, (specialty, area) in SYMPTOM_SPECIALTY_MAP.items():
        if kw in q:
            entry = entries.setdefault(
                specialty, {"specialty": specialty, "risk_area": area, "matched_symptoms": []}
            )
            entry["matched_symptoms"].append(kw)

    results = sorted(entries.values(), key=lambda e: -len(e["matched_symptoms"]))
    for entry in results:
        matched = ", ".join(sorted(set(entry["matched_symptoms"])))
        entry["reason"] = (
            f"You mentioned {matched}. {entry['specialty']} is the specialty that "
            f"usually evaluates this. Describe your symptoms to a qualified doctor "
            f"for an actual assessment."
        )
    return results


def now_iso() -> str:
    return datetime.now().isoformat()
