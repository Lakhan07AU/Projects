"""AI assistant, consents, data export, account management."""
import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import AppError
from app.models import (
    AIConversation,
    AIMessage,
    Consent,
    Doctor,
    EmergencyContact,
    FamilyCondition,
    FamilyMember,
    HealthMetricValue,
    MedicalReport,
    Reminder,
    User,
)
from app.schemas.schemas import ChatIn, ChatMessageOut, ConsentIn
from app.services.assistant import chat as assistant_chat

router = APIRouter(tags=["assistant & account"])


# ---------------- AI Assistant ----------------
@router.post("/assistant/chat")
def assistant_send(
    payload: ChatIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conversation = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == user.id)
        .order_by(AIConversation.created_at.desc())
        .first()
    )
    if not conversation:
        conversation = AIConversation(user_id=user.id, title=payload.message[:60])
        db.add(conversation)
        db.commit()

    reply = assistant_chat(db, user.id, payload.message, conversation)
    return {"reply": reply.content, "safety_filtered": reply.safety_filtered}


@router.get("/assistant/history", response_model=list[ChatMessageOut])
def assistant_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conversation = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == user.id)
        .order_by(AIConversation.created_at.desc())
        .first()
    )
    if not conversation:
        return []
    messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.id.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(messages))


@router.delete("/assistant/history", status_code=204)
def clear_assistant_history(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.query(AIMessage).filter(
        AIMessage.conversation_id.in_(
            db.query(AIConversation.id).filter(AIConversation.user_id == user.id)
        )
    ).delete(synchronize_session=False)
    db.query(AIConversation).filter(AIConversation.user_id == user.id).delete(synchronize_session=False)
    db.commit()


# ---------------- Consents ----------------
@router.put("/consents", response_model=ConsentIn)
def set_consent(
    payload: ConsentIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    allowed = {
        "location_access", "contact_import", "medical_data_processing",
        "ai_analysis", "data_sharing", "notifications",
    }
    if payload.consent_type not in allowed:
        raise AppError("INVALID_CONSENT_TYPE", "Unknown consent type.", 400)
    row = Consent(
        user_id=user.id, consent_type=payload.consent_type,
        granted=payload.granted, version="1.0",
    )
    db.add(row)  # append-only history; latest wins at read time
    db.commit()
    audit(request, db, user.id, "CONSENT_UPDATED", "consent",
          metadata={"type": payload.consent_type, "granted": payload.granted})
    return payload


@router.get("/consents")
def list_consents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    latest: dict[str, Consent] = {}
    for c in db.query(Consent).filter(Consent.user_id == user.id).order_by(Consent.granted_at):
        latest[c.consent_type] = c
    return [
        {"consent_type": k, "granted": v.granted, "version": v.version, "granted_at": v.granted_at}
        for k, v in sorted(latest.items())
    ]


# ---------------- Data export ----------------
@router.get("/export/json")
def export_json(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    def dump(model, order_by):
        rows = db.query(model).filter(getattr(model, "user_id") == user.id).order_by(order_by).all()
        out = []
        for r in rows:
            d = {}
            for col in r.__table__.columns:
                val = getattr(r, col.name)
                d[col.name] = str(val) if hasattr(val, "isoformat") else val
            out.append(d)
        return out

    family_members = []
    members = db.query(FamilyMember).filter(FamilyMember.user_id == user.id).all()
    for m in members:
        conditions = [
            {"condition_name": fc.condition_name, "diagnosis_age": fc.diagnosis_age}
            for fc in db.query(FamilyCondition).filter(FamilyCondition.member_id == m.id).all()
        ]
        family_members.append({
            "relationship": m.relationship, "name": m.name,
            "living_status": m.living_status.value if hasattr(m.living_status, "value") else str(m.living_status),
            "conditions": conditions,
        })

    data = {
        "export_note": "This export was generated by HealthSphere from your account records.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": _profile_dict(db, user),
        "family_members": family_members,
        "reports": [
            {"id": r.id, "file_name": r.file_name, "category": r.category,
             "report_date": str(r.report_date), "status": r.status.value if hasattr(r.status, "value") else str(r.status)}
            for r in db.query(MedicalReport).filter(MedicalReport.user_id == user.id).all()
        ],
        "health_metric_values": dump(HealthMetricValue, HealthMetricValue.recorded_at),
        "reminders": dump(Reminder, Reminder.due_at),
        "doctors": dump(Doctor, Doctor.doctor_name),
        "emergency_contacts": dump(EmergencyContact, EmergencyContact.priority),
    }

    audit(request, db, user.id, "DATA_EXPORTED", metadata={"format": "json"})
    content = json.dumps(data, indent=2, default=str)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="healthsphere_export.json"'},
    )


@router.get("/export/metrics.csv")
def export_metrics_csv(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["metric_key", "value", "secondary_value", "unit", "recorded_at", "source"])
    rows = (
        db.query(HealthMetricValue)
        .filter(HealthMetricValue.user_id == user.id)
        .order_by(HealthMetricValue.recorded_at)
        .all()
    )
    for r in rows:
        writer.writerow([r.metric_key, r.value, r.secondary_value, r.unit, r.recorded_at.isoformat(), r.source])

    audit(request, db, user.id, "DATA_EXPORTED", metadata={"format": "csv"})
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="healthsphere_metrics.csv"'},
    )


def _profile_dict(db: Session, user: User) -> dict:
    from app.clinical.preventive import calculate_age, calculate_bmi
    from app.models import UserProfile

    p = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not p:
        return {}
    data = {}
    for col in p.__table__.columns:
        val = getattr(p, col.name)
        data[col.name] = str(val) if hasattr(val, "isoformat") else val
    data["age"] = calculate_age(p.date_of_birth)
    data["bmi"] = calculate_bmi(p.height_cm, p.weight_kg)
    return data


# ---------------- Account deletion ----------------
@router.post("/account/delete-request")
def request_account_deletion(
    request: Request,
    confirm_text: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Permanent deletion (soft-deactivate now; purge job removes content).

    Requires the user to type DELETE to confirm. An optional export should be
    downloaded first — deletion is irreversible.
    """
    if confirm_text.strip().upper() != "DELETE":
        raise AppError("CONFIRMATION_REQUIRED", 'Type "DELETE" to confirm permanent deletion.', 400)

    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    # revoke sessions
    from app.models import RefreshSession

    for s in db.query(RefreshSession).filter(RefreshSession.user_id == user.id, RefreshSession.revoked_at.is_(None)):
        s.revoked_at = datetime.now(timezone.utc)
    db.commit()
    audit(request, db, user.id, "ACCOUNT_DELETION_REQUESTED")
    return {
        "success": True,
        "note": "Your account has been deactivated and scheduled for deletion. "
                "Associated personal data will be purged per retention policy.",
    }
