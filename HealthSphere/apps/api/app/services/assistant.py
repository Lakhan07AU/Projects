"""AI health assistant: intent → least-data retrieval → generation → safety."""
import json
import logging

from sqlalchemy.orm import Session

from app.ai import base as ai_base
from app.models import (
    AIMessage,
    AIConversation,
    HealthMetricValue,
    MedicalEntity,
    MedicalReport,
    Reminder,
)

logger = logging.getLogger("healthsphere.assistant")

DENY_PATTERNS = [
    "diagnose", "prescribe", "should i take", "which medicine",
    "stop my", "dosage", "what disease", "what condition",
    "do i have", "medicine", "medication",
    "absolutely need", "must see", "which doctor i", "which specialist i",
    "force you to refer", "refer me",
]

EMERGENCY_PATTERNS = [
    "chest pain", "can't breathe", "cant breathe", "cannot breathe",
    "difficulty breathing", "shortness of breath", "heart attack",
    "stroke", "unconscious", "seizure", "heavy bleeding", "suicid",
    "overdose",
]

EMERGENCY_REPLY = (
    "These symptoms can indicate a medical emergency. Please call your local "
    "emergency number (108 or 112 in India, 911 in the US) or go to the nearest "
    "hospital immediately. Do not wait for an online answer."
)

SAFE_DENY = (
    "I can't diagnose conditions or advise about medications — those decisions "
    "need a qualified healthcare professional who knows your full history. I can "
    "help you review your own records, show trends, or suggest topics to discuss "
    "with your doctor."
)


def _retrieve_context(db: Session, user_id: int, question: str) -> dict:
    q = question.lower()
    context: dict = {}

    wants_reports = any(k in q for k in ["report", "blood", "lab", "result", "latest", "changed"])
    wants_trends = any(k in q for k in ["trend", "changed", "history", "over time"])
    wants_reminders = any(k in q for k in ["reminder", "upcoming", "due"])

    # When the user asks why a specialty was suggested, retrieve the actual
    # stored specialist suggestions — the assistant must explain them, never
    # invent different ones.
    if any(k in q for k in ["specialist", "suggested", "why was", "why is",
                            "recommendation", "cardiolog", "dermatolog", "endocrin"]):
        from app.models import SpecialistRecommendation

        recs = (
            db.query(SpecialistRecommendation)
            .filter(SpecialistRecommendation.user_id == user_id)
            .order_by(SpecialistRecommendation.created_at.desc())
            .limit(5)
            .all()
        )
        context["specialist_suggestions"] = [
            {
                "specialty": r.specialty_name,
                "relevance": r.relevance,
                "reason_on_record": r.reason,
                "created_at": r.created_at.isoformat(),
            }
            for r in recs
        ]

    if wants_reports:
        report = (
            db.query(MedicalReport)
            .filter(MedicalReport.user_id == user_id)
            .order_by(MedicalReport.created_at.desc())
            .first()
        )
        if report:
            entities = db.query(MedicalEntity).filter(MedicalEntity.report_id == report.id).limit(15).all()
            prev = (
                db.query(MedicalReport)
                .filter(
                    MedicalReport.user_id == user_id,
                    MedicalReport.id != report.id,
                    MedicalReport.category == report.category,
                )
                .order_by(MedicalReport.created_at.desc())
                .first()
            )
            prev_entities = []
            if prev:
                rows = db.query(MedicalEntity).filter(MedicalEntity.report_id == prev.id).limit(15).all()
                prev_entities = [{"test_name": e.test_name, "value": e.value} for e in rows]
            context["latest_report"] = {
                "date": str(report.report_date or report.created_at.date()),
                "category": report.category,
                "result_count": len(entities),
                "results": [
                    {
                        "test_name": e.test_name,
                        "value": e.value,
                        "unit": e.unit,
                        "abnormal_flag": e.abnormal_flag,
                    }
                    for e in entities[:10]
                ],
                "previous_results": prev_entities[:10],
            }

    if wants_trends or not context:
        from sqlalchemy import func

        rows = (
            db.query(
                HealthMetricValue.metric_key,
                func.count(HealthMetricValue.id),
                func.min(HealthMetricValue.value),
                func.max(HealthMetricValue.value),
                func.min(HealthMetricValue.recorded_at),
                func.max(HealthMetricValue.recorded_at),
            )
            .filter(HealthMetricValue.user_id == user_id)
            .group_by(HealthMetricValue.metric_key)
            .all()
        )
        trends = [
            {
                "metric": r[0],
                "data_points": int(r[1]),
                "min": float(r[2]),
                "max": float(r[3]),
                "direction": _simple_direction(r[0], user_id, db),
            }
            for r in rows
        ]
        context["trends"] = trends[:6]
        if not wants_trends and not wants_reports:
            # strip detail; keep summary only
            for t in trends:
                t.pop("min", None)
                t.pop("max", None)

    if wants_reminders:
        reminders = (
            db.query(Reminder)
            .filter(Reminder.user_id == user_id, Reminder.status == "open")
            .order_by(Reminder.due_at.asc())
            .limit(5)
            .all()
        )
        context["upcoming_reminders"] = [
            {"title": r.title, "due_at": r.due_at.isoformat()} for r in reminders
        ]

    return context


def _simple_direction(metric_key: str, user_id: int, db: Session) -> str:
    from app.services.trends import TrendPoint, analyze_trend

    rows = (
        db.query(HealthMetricValue.recorded_at, HealthMetricValue.value)
        .filter(HealthMetricValue.user_id == user_id, HealthMetricValue.metric_key == metric_key)
        .order_by(HealthMetricValue.recorded_at.asc())
        .all()
    )
    result = analyze_trend([TrendPoint(d, v) for d, v in rows])
    return result.direction


def chat(db: Session, user_id: int, question: str, conversation: AIConversation) -> AIMessage:
    # Input guard: refuse clearly unsafe intents before any retrieval.
    lowered = question.lower()
    safety_filtered = False
    if len(question) > 2000:
        question = question[:2000]

    db.add(AIMessage(conversation_id=conversation.id, role="user", content=question))

    # Emergency escalation happens first — it never depends on the AI provider.
    if any(p in lowered for p in EMERGENCY_PATTERNS):
        msg = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=EMERGENCY_REPLY,
            safety_filtered=True,
        )
        db.add(msg)
        db.commit()
        return msg

    context = _retrieve_context(db, user_id, question)
    try:
        provider = ai_base.get_ai_provider()
        reply = provider.assistant_reply(question, json.dumps(context, default=str))
        content = reply.content
        if any(p in lowered for p in DENY_PATTERNS):
            content = SAFE_DENY + "\n\n" + content
            safety_filtered = True
    except Exception:
        logger.exception("Assistant provider failed")
        content = (
            "I'm temporarily unable to analyze your records right now. Your data is safe "
            "and you can try again shortly. For anything urgent please contact a "
            "healthcare professional."
        )

    msg = AIMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=content,
        safety_filtered=safety_filtered,
    )
    db.add(msg)
    db.commit()
    return msg
