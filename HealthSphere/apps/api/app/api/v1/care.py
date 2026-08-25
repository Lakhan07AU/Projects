"""Doctors, emergency contacts, emergency alerts, reminders, notifications, discovery."""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import AppError, NotFoundError
from app.models import (
    Doctor,
    EmergencyAlert,
    EmergencyContact,
    Hospital,
    Notification,
    Reminder,
    User,
    UserProfile,
)
from app.schemas.schemas import (
    DoctorIn,
    DoctorOut,
    EmergencyContactIn,
    EmergencyContactOut,
    ReminderIn,
    ReminderOut,
    ReminderUpdateIn,
)

router = APIRouter(tags=["care"])


# ---------------- Doctor search (declared before /doctors/{doctor_id}) ----------------
@router.get("/doctors/search")
def search_doctors(
    specialty: str | None = Query(None, max_length=128),
    q: str | None = Query(None, max_length=128),
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
    radius_km: float = Query(10, gt=0, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Find doctors/facilities by specialty and optional location.

    Searches only records that already exist in HealthSphere — the user's own
    saved doctors plus previously cached discovery facilities. No fabricated
    provider data.
    """
    term = (specialty or q or "").strip()
    my_doctors = []
    if term:
        query = db.query(Doctor).filter(Doctor.user_id == user.id)
        if specialty:
            query = query.filter(Doctor.specialty.ilike(f"%{specialty.strip()}%"))
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                Doctor.doctor_name.ilike(like)
                | Doctor.clinic.ilike(like)
                | Doctor.specialty.ilike(like)
            )
        rows = query.order_by(Doctor.is_family_doctor.desc()).limit(25).all()
        my_doctors = [
            {
                "id": d.id,
                "doctor_name": d.doctor_name,
                "specialty": d.specialty,
                "clinic": d.clinic,
                "phone": d.phone,
                "is_family_doctor": d.is_family_doctor,
            }
            for d in rows
        ]

    facilities = []
    if term:
        from math import asin, cos, radians, sin, sqrt

        def _dist(h_lat, h_lon):
            if h_lat is None or h_lon is None or lat is None or lon is None:
                return None
            phi1, phi2 = radians(lat), radians(h_lat)
            dphi = radians(h_lat - lat)
            dlmb = radians(h_lon - lon)
            a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlmb / 2) ** 2
            return round(6371 * 2 * asin(sqrt(a)), 1)

        frows = (
            db.query(Hospital)
            .filter(
                Hospital.kind.in_(["hospital", "clinic"]),
                Hospital.name.ilike(f"%{term}%") | Hospital.services.ilike(f"%{term}%"),
            )
            .limit(25)
            .all()
        )
        for h in frows:
            distance = _dist(h.latitude, h.longitude)
            if lat is not None and lon is not None:
                # location given: respect the radius, nearest first
                if distance is None or distance > radius_km:
                    continue
            facilities.append({
                "name": h.name,
                "kind": h.kind,
                "address": h.address,
                "phone": h.phone,
                "latitude": h.latitude,
                "longitude": h.longitude,
                "services": h.services,
                "distance_km": distance,
            })
        facilities.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0))

    return {"query": {"specialty": specialty, "q": q},
            "my_doctors": my_doctors, "facilities": facilities}


# ---------------- Doctors ----------------
@router.get("/doctors", response_model=list[DoctorOut])
def list_doctors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Doctor)
        .filter(Doctor.user_id == user.id)
        .order_by(Doctor.is_family_doctor.desc(), Doctor.doctor_name)
        .all()
    )


@router.post("/doctors", response_model=DoctorOut, status_code=201)
def add_doctor(
    payload: DoctorIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.is_family_doctor:
        # Only one family doctor at a time.
        db.query(Doctor).filter(Doctor.user_id == user.id).update({"is_family_doctor": False})
    _ensure_no_duplicate_doctor(db, user.id, payload)
    row = Doctor(user_id=user.id, **payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(
            "CONFLICT",
            "A doctor with this name and clinic already exists in your care team",
            409,
        )
    audit(request, db, user.id, "DOCTOR_ADDED", "doctor", row.id)
    return row


@router.get("/doctors/{doctor_id}", response_model=DoctorOut)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _owned(db.get(Doctor, doctor_id), user.id)


@router.post("/doctors/{doctor_id}/family-doctor", response_model=DoctorOut)
def set_family_doctor(
    doctor_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Designate (or remove) this doctor as the user's single Family Doctor."""
    row = _owned(db.get(Doctor, doctor_id), user.id)
    make_family = not row.is_family_doctor
    if make_family:
        # Exactly one active Family Doctor at a time.
        db.query(Doctor).filter(Doctor.user_id == user.id).update({"is_family_doctor": False})
    row.is_family_doctor = make_family
    db.commit()
    audit(request, db, user.id, "FAMILY_DOCTOR_SET" if make_family else "FAMILY_DOCTOR_REMOVED",
          "doctor", doctor_id)
    return row


@router.put("/doctors/{doctor_id}", response_model=DoctorOut)
def update_doctor(
    doctor_id: int,
    payload: DoctorIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(Doctor, doctor_id), user.id)
    if payload.is_family_doctor:
        db.query(Doctor).filter(Doctor.user_id == user.id).update({"is_family_doctor": False})
    _ensure_no_duplicate_doctor(db, user.id, payload, exclude_id=doctor_id)
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(
            "CONFLICT",
            "A doctor with this name and clinic already exists in your care team",
            409,
        )
    audit(request, db, user.id, "DOCTOR_UPDATED", "doctor", doctor_id)
    return row


@router.delete("/doctors/{doctor_id}", status_code=204)
def delete_doctor(
    doctor_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(Doctor, doctor_id), user.id)
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "DOCTOR_DELETED", "doctor", doctor_id)


# ---------------- Emergency contacts ----------------
@router.get("/emergency-contacts", response_model=list[EmergencyContactOut])
def list_contacts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(EmergencyContact)
        .filter(EmergencyContact.user_id == user.id)
        .order_by(EmergencyContact.priority, EmergencyContact.name)
        .all()
    )


@router.post("/emergency-contacts", response_model=EmergencyContactOut, status_code=201)
def add_contact(
    payload: EmergencyContactIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = EmergencyContact(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    audit(request, db, user.id, "CONTACT_ADDED", "emergency_contact", row.id)
    return row


@router.put("/emergency-contacts/{contact_id}", response_model=EmergencyContactOut)
def update_contact(
    contact_id: int,
    payload: EmergencyContactIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(EmergencyContact, contact_id), user.id)
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.commit()
    audit(request, db, user.id, "CONTACT_UPDATED", "emergency_contact", contact_id)
    return row


@router.delete("/emergency-contacts/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(EmergencyContact, contact_id), user.id)
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "CONTACT_DELETED", "emergency_contact", contact_id)


# ---------------- Reminders ----------------
RECURRENCE_NEXT = {"daily": 1, "weekly": 7, "monthly": 30}


@router.get("/reminders", response_model=list[ReminderOut])
def list_reminders(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Reminder).filter(Reminder.user_id == user.id)
    if status_filter:
        query = query.filter(Reminder.status == status_filter)
    return query.order_by(Reminder.due_at.asc()).limit(200).all()


@router.post("/reminders", response_model=ReminderOut, status_code=201)
def create_reminder(
    payload: ReminderIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = Reminder(user_id=user.id, source="user", **payload.model_dump())
    db.add(row)
    db.commit()
    audit(request, db, user.id, "REMINDER_CREATED", "reminder", row.id)
    return row


@router.put("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(Reminder, reminder_id), user.id)
    data = payload.model_dump(exclude_unset=True)

    if data.get("due_at"):
        row.due_at = data["due_at"]
        row.status = "open"
    if data.get("status") == "done":
        row.status = "done"
        recurrence = RECURRENCE_NEXT.get(row.recurrence.value if hasattr(row.recurrence, "value") else str(row.recurrence))
        if recurrence:
            # recurring reminders automatically reschedule after completion
            nxt = Reminder(
                user_id=row.user_id, type=row.type, title=row.title, description=row.description,
                due_at=datetime.fromtimestamp(row.due_at.timestamp() + recurrence * 86400),
                recurrence=row.recurrence, status="open", source=row.source,
            )
            db.add(nxt)
    elif data.get("status") in ("cancelled",):
        row.status = data["status"]

    db.commit()
    audit(request, db, user.id, "REMINDER_UPDATED", "reminder", reminder_id, {"status": row.status})
    return row


@router.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned(db.get(Reminder, reminder_id), user.id)
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "REMINDER_DELETED", "reminder", reminder_id)


# ---------------- Notifications ----------------
@router.get("/notifications")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": n.id, "title": n.title, "body": n.body, "channel": n.channel,
            "read_at": n.read_at, "created_at": n.created_at,
        }
        for n in rows
    ]


# ---------------- Emergency mode ----------------
def _alert_out(alert: EmergencyAlert) -> dict:
    return {
        "id": alert.id,
        "status": alert.status,
        "notified": json.loads(alert.notified_names or "[]"),
        "message_sent": alert.message,
        "triggered_at": alert.triggered_at,
        "cancelled_at": alert.cancelled_at,
    }


@router.post("/emergency/trigger", status_code=201)
def trigger_emergency_alert(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """SOS: notify registered contacts with a medical card. No AI involved."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    contacts = (
        db.query(EmergencyContact)
        .filter(EmergencyContact.user_id == user.id)
        .order_by(EmergencyContact.priority, EmergencyContact.name)
        .all()
    )

    lines = [f"EMERGENCY ALERT â€” {user.full_name or user.email} needs urgent help."]
    if profile:
        if getattr(profile, "blood_group", None):
            lines.append(f"Blood group: {profile.blood_group}")
        if getattr(profile, "allergies", None):
            lines.append(f"Allergies: {profile.allergies}")
        if getattr(profile, "emergency_information", None):
            lines.append(f"Additional info: {profile.emergency_information}")
    lines.append("Please attempt to reach them and send help to their last known location.")
    message = "\n".join(lines)

    names = [c.name for c in contacts]
    alert = EmergencyAlert(
        user_id=user.id,
        status="sent" if contacts else "pending",
        notified_names=json.dumps(names),
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    audit(request, db, user.id, "EMERGENCY_TRIGGERED", "emergency_alert", alert.id,
          {"notified_count": len(names)})
    return _alert_out(alert)


@router.get("/emergency/alerts")
def list_emergency_alerts(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    rows = (
        db.query(EmergencyAlert)
        .filter(EmergencyAlert.user_id == user.id)
        .order_by(EmergencyAlert.triggered_at.desc())
        .limit(50)
        .all()
    )
    return [_alert_out(a) for a in rows]


@router.post("/emergency/alerts/{alert_id}/cancel")
def cancel_emergency_alert(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    alert = _owned(db.get(EmergencyAlert, alert_id), user.id)
    alert.status = "cancelled"
    alert.cancelled_at = datetime.now()
    db.commit()
    audit(request, db, user.id, "EMERGENCY_CANCELLED", "emergency_alert", alert_id)
    return _alert_out(alert)


# ---------------- Healthcare discovery ----------------
@router.get("/healthcare/nearby")
def nearby_healthcare(
    request: Request,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    kind: str = Query("all", pattern="^(all|hospital|clinic|lab|pharmacy)$"),
    radius_km: float = Query(10, gt=0, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.services.notifications import get_map_provider

    provider = get_map_provider()
    results = provider.nearby(lat, lon, kind, radius_km)
    return {
        "results": results,
        "note": (
            "Location results are sample development data."
            if provider.__class__.__name__.startswith("Mock")
            else f"Results provided by {provider.__class__.__name__}."
        ),
    }


def _owned(obj, user_id: int):
    if not obj or obj.user_id != user_id:
        raise NotFoundError("Resource not found")
    return obj


def _ensure_no_duplicate_doctor(db: Session, user_id: int, payload: DoctorIn,
                                exclude_id: int | None = None) -> None:
    """Case-insensitive duplicate check; NULL clinics compare as empty strings
    (a plain UNIQUE constraint never fires when the clinic is NULL)."""
    query = db.query(Doctor).filter(
        Doctor.user_id == user_id,
        func.lower(Doctor.doctor_name) == payload.doctor_name.strip().lower(),
        func.coalesce(Doctor.clinic, "") == (payload.clinic or "").strip(),
    )
    if exclude_id is not None:
        query = query.filter(Doctor.id != exclude_id)
    if query.first():
        raise AppError(
            "CONFLICT",
            "A doctor with this name and clinic already exists in your care team",
            409,
        )
