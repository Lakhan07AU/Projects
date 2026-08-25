"""Specialist suggestion engine (Doctor & Specialist section).

Pipeline: user context → symptom/condition normalization → DB-driven
specialty mapping → context ranking → safety validation → persisted
suggestion. Deterministic rules are the decision-maker; the LLM only
explains stored results later. This is healthcare navigation support,
never a diagnosis or a referral.
"""
import json
import logging
import re

from sqlalchemy.orm import Session

from app.models import (
    ConditionSpecialtyMap,
    Doctor,
    SpecialistRecommendation,
    Specialty,
    Symptom,
    SymptomSpecialtyMap,
    UserCondition,
    UserSymptom,
)
from app.services.timeline import TimelineEventType, add_event

logger = logging.getLogger("healthsphere.specialists")

RELEVANCE_SCORE = {"high": 30, "medium": 20, "low": 10}
SEVERITY_BONUS = {"mild": 0, "moderate": 5, "severe": 12}
CHRONIC_PATTERN = re.compile(r"\b(week|month|year)s?\b", re.IGNORECASE)
CHRONIC_BONUS = 6

# Clearly urgent symptom combinations / single red flags. When detected we
# stop normal navigation and surface emergency guidance immediately.
RED_FLAG_COMBOS = [
    ("chest", ["breathless", "shortness of breath", "sweat", "radiat", "jaw", "faint"]),
]
RED_FLAG_SINGLE = [
    "crushing chest pain",
    "coughing blood",
    "coughing up blood",
    "blood in vomit",
    "vomiting blood",
    "severe bleeding",
    "unconscious",
    "slurred speech",
    "sudden weakness on one side",
    "weakness on one side",
    "loss of consciousness",
]

RED_FLAG_MESSAGE = (
    "Potential emergency indicator detected.\n\n"
    "Please seek urgent medical attention according to your local emergency "
    "guidance."
)

INSUFFICIENT_MESSAGE = (
    "Insufficient information for a personalized specialist suggestion. "
    "Consider starting with a primary-care physician if you have a health concern."
)


def check_red_flags(text: str) -> str | None:
    """Return the matched red-flag phrase if clearly urgent indicators appear."""
    q = f" {text.lower().strip()} "
    for anchor, followers in RED_FLAG_COMBOS:
        if anchor in q and any(f in q for f in followers):
            return anchor
    for phrase in RED_FLAG_SINGLE:
        if phrase in q:
            return phrase
    return None


def _map_symptoms(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(UserSymptom, Symptom)
        .outerjoin(Symptom, UserSymptom.symptom_id == Symptom.id)
        .filter(UserSymptom.user_id == user_id)
        .order_by(UserSymptom.created_at.desc())
        .all()
    )
    symptoms = []
    for us, catalog in rows:
        name = (catalog.name if catalog else us.symptom_name) or us.symptom_name
        symptoms.append({
            "name": name.lower(),
            "severity": us.severity.value if hasattr(us.severity, "value") else str(us.severity),
            "duration_text": us.duration_text or "",
            "chronic": bool(us.duration_text and CHRONIC_PATTERN.search(us.duration_text)),
            "notes": (us.notes or "").lower(),
        })
    return symptoms


def analyze_specialist_needs(db: Session, user) -> dict:
    """Build, rank, validate and persist specialty suggestions."""
    from app.clinical.preventive import build_health_context

    symptoms = _map_symptoms(db, user.id)
    conditions = [
        c.condition_name.lower()
        for c in db.query(UserCondition).filter(UserCondition.user_id == user.id).all()
    ]
    ctx = build_health_context(db, user)

    combined_text = " ".join(
        [s["name"] + " " + s["notes"] for s in symptoms] + conditions
    )
    red_flag = check_red_flags(combined_text)
    if red_flag:
        return {
            "red_flag": True,
            "message": RED_FLAG_MESSAGE,
            "matched_indicator": red_flag,
            "recommendations": [],
            "family_doctor": None,
        }

    # ---- scoring across mapping tables + existing report/trend context ----
    scores: dict[int, dict] = {}

    def add(specialty: Specialty | None, relevance: str, weight: float,
           rule_key: str, reason: str) -> None:
        if specialty is None:
            return
        entry = scores.setdefault(specialty.id, {"specialty": specialty, "score": 0.0,
                                                 "relevance": "low", "reasons": [],
                                                 "rules": []})
        entry["score"] += RELEVANCE_SCORE.get(relevance, 10) * weight
        if rule_key not in entry["rules"]:
            entry["rules"].append(rule_key)
        if reason not in entry["reasons"]:
            entry["reasons"].append(reason)
        new_rel = relevance if RELEVANCE_SCORE.get(relevance, 0) > RELEVANCE_SCORE.get(entry["relevance"], 0) else entry["relevance"]
        entry["relevance"] = new_rel

    catalog_by_key = {s.key: s for s in db.query(Symptom).all()}
    map_rows = db.query(SymptomSpecialtyMap, Specialty, Symptom).join(
        Specialty, SymptomSpecialtyMap.specialty_id == Specialty.id
    ).join(Symptom, SymptomSpecialtyMap.symptom_id == Symptom.id).all()
    maps_by_key: dict[str, list[tuple]] = {}
    for m, specialty, symptom in map_rows:
        maps_by_key.setdefault(symptom.key, []).append((m.relevance, specialty))

    matched: dict[str, dict] = {}
    STOP_WORDS = {"or", "and", "the", "of", "in"}
    for s in symptoms:
        reported_words = set(s["name"].replace("-", " ").split()) - STOP_WORDS
        for key, row in catalog_by_key.items():
            catalog_words = set(row.name.lower().replace("-", " ").split()) - STOP_WORDS
            overlap = catalog_words & reported_words
            if len(overlap) >= max(1, min(len(catalog_words), len(reported_words)) - 1):
                matched[key] = s
                break

    for key, s in matched.items():
        for relevance, specialty in maps_by_key.get(key, []):
            weight = 1.0
            bonus_reason = ""
            if SEVERITY_BONUS.get(s["severity"], 0):
                weight += SEVERITY_BONUS[s["severity"]] / 100
                if s["severity"] == "severe":
                    bonus_reason = " (reported as severe)"
            if s["chronic"]:
                weight += CHRONIC_BONUS / 100
                bonus_reason += " (persisting over time)"
            add(specialty, relevance, weight, f"symptom-mapping:{key}",
                f"your reported symptom \u201c{s['name']}\u201d{bonus_reason}")

    cond_rows = db.query(ConditionSpecialtyMap, Specialty).join(
        Specialty, ConditionSpecialtyMap.specialty_id == Specialty.id
    ).all()
    family_keywords = ctx.get("family_condition_keywords", [])
    for m, specialty in cond_rows:
        kw = m.condition_keyword.lower()
        for c in conditions:
            if kw in c:
                add(specialty, m.relevance, 1.0, f"condition-mapping:{kw}",
                    f"your recorded condition \u201c{c}\u201d")
                break
        for fk in family_keywords:
            if kw in fk:
                # Family history is contextual, never proof of disease.
                add(specialty, "low", 0.5, f"family-history:{kw}",
                    f"a family history of \u201c{fk}\u201d (contextual factor only)")
                break

    # Existing report findings / trends via the established preventive engine.
    from app.clinical.preventive import recommend_specialties

    for extra in recommend_specialties(ctx):
        specialty = next(
            (sp for sp in db.query(Specialty).all() if sp.name == extra["specialty"]), None
        )
        if specialty is None:
            continue
        relevance = "high" if extra["confidence"] >= 0.7 else "medium"
        rule_key = f"report-context:{extra['risk_area']}"
        if rule_key not in scores.get(specialty.id, {}).get("rules", []):
            add(specialty, relevance, 1.0, rule_key,
                f"findings in your records ({extra['risk_area'].replace('_', ' ')})")

    has_any_input = bool(symptoms or conditions or ctx.get("flagged_test_keywords")
                         or ctx.get("latest_blood_pressure_systolic") or ctx.get("latest_hba1c"))

    primary = db.query(Specialty).filter(Specialty.key == "primary-care").first()

    if not scores or not has_any_input:
        return {
            "red_flag": False,
            "insufficient_info": True,
            "message": INSUFFICIENT_MESSAGE,
            "recommendations": [],
            "family_doctor": _family_doctor(db, user.id),
        }

    ranked = sorted(scores.values(), key=lambda e: (-e["score"], e["specialty"].name))
    top = ranked[:4]
    if primary and all(e["specialty"].id != primary.id for e in top):
        # Primary care is always available as the general entry point (§16).
        top.append({"specialty": primary, "score": 0, "relevance": "medium",
                    "reasons": [], "rules": ["primary-care-fallback"]})

    family_doctor = _family_doctor(db, user.id)
    results = []
    for entry in top:
        reasons = entry["reasons"] or []
        reason_text = "; ".join(reasons[:3]) if reasons else (
            "a general starting point to discuss your concerns"
        )
        if family_doctor and entry["specialty"].key != "primary-care":
            first_step = (
                f" Your Family Doctor, {family_doctor['doctor_name']}, may be a good "
                f"first point of discussion."
            )
        else:
            first_step = ""
        reason = (
            f"The information in your records suggests this specialty may be "
            f"appropriate to discuss with a qualified healthcare professional — "
            f"{reason_text}.{first_step}"
        )
        rec = SpecialistRecommendation(
            user_id=user.id,
            specialty_id=entry["specialty"].id,
            specialty_name=entry["specialty"].name,
            relevance=entry["relevance"],
            reason=reason,
            source_rules=json.dumps(entry["rules"]),
            input_context=json.dumps({
                "symptoms": [s["name"] for s in symptoms][:10],
                "conditions": conditions[:10],
                "family_history": family_keywords[:6],
                "flagged_tests": ctx.get("flagged_test_keywords", [])[:6],
                "age": ctx.get("age"),
            }),
        )
        db.add(rec)
        db.flush()
        add_event(
            db,
            user_id=user.id,
            event_type=TimelineEventType.recommendation,
            title="Specialist Recommendation Created",
            description=f"{rec.specialty_name} ({rec.relevance} relevance): {reason}",
            source="specialist_engine",
            related_entity_type="specialist_recommendation",
            related_entity_id=rec.id,
        )
        results.append(rec)
    db.commit()
    return {
        "red_flag": False,
        "insufficient_info": False,
        "message": None,
        "recommendations": [_rec_out(r) for r in results],
        "family_doctor": family_doctor,
    }


def _rec_out(r: SpecialistRecommendation) -> dict:
    return {
        "id": r.id,
        "specialty_id": r.specialty_id,
        "specialty_name": r.specialty_name,
        "relevance": r.relevance,
        "reason": r.reason,
        "source_rules": json.loads(r.source_rules or "[]"),
        "status": r.status,
        "created_at": r.created_at,
    }


def _family_doctor(db: Session, user_id: int) -> dict | None:
    doc = (
        db.query(Doctor)
        .filter(Doctor.user_id == user_id, Doctor.is_family_doctor.is_(True))
        .first()
    )
    if not doc:
        return None
    return {
        "id": doc.id,
        "doctor_name": doc.doctor_name,
        "specialty": doc.specialty,
        "clinic": doc.clinic,
        "phone": doc.phone,
    }
