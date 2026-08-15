"""Pothole management endpoints (government/admin) and public reads."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_government
from app.core.enums import PotholeStatus, Priority, Role
from app.db.database import get_db
from app.db.models import Pothole, Repair, User
from app.schemas.pothole import (
    AssignRequest,
    OverridePriorityRequest,
    PotholeDetail,
    PotholeOut,
    UpdateStatusRequest,
    VerifyRequest,
)
from app.services.audit import audit
from app.services.priority import compute_priority, pending_days_since
from app.services.repair_workflow import assign_team, change_pothole_status
from app.services.road_health import compute_road_health
from app.utils.errors import bad_request, not_found

router = APIRouter(prefix="/api/potholes", tags=["potholes"])


def _get_or_404(db: Session, pothole_id: str) -> Pothole:
    pothole = db.query(Pothole).filter(Pothole.id == pothole_id).first()
    if not pothole:
        raise not_found("Pothole not found")
    return pothole


@router.get("", response_model=list[PotholeOut])
def list_potholes(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    severity: str | None = None,
    status: str | None = None,
    ward: str | None = None,
    road: str | None = None,
    search: str | None = None,
    limit: int = 200,
    offset: int = 0,
):
    query = db.query(Pothole)
    if severity:
        query = query.filter(Pothole.severity == severity.upper())
    if status:
        query = query.filter(Pothole.status == status.upper())
    if ward:
        query = query.filter(Pothole.ward == ward)
    if road:
        query = query.filter(Pothole.road == road)
    if search:
        query = query.filter(
            or_(Pothole.pothole_code.ilike(f"%{search}%"), Pothole.road.ilike(f"%{search}%"))
        )
    return query.order_by(Pothole.created_at.desc()).limit(min(limit, 500)).offset(offset).all()


@router.get("/{pothole_id}", response_model=PotholeDetail)
def get_pothole(pothole_id: str, db: Session = Depends(get_db),
                _: User = Depends(get_current_user)):
    pothole = _get_or_404(db, pothole_id)
    return pothole


@router.post("/{pothole_id}/verify", response_model=PotholeOut)
def verify_or_reject(
    pothole_id: str,
    payload: VerifyRequest,
    user: User = Depends(require_government),
    db: Session = Depends(get_db),
):
    pothole = _get_or_404(db, pothole_id)
    if payload.action == "verify":
        pothole.verified_by = user.name
        pothole.verified_at = datetime.utcnow()
        audit(db, user.id, user.name, "pothole_verified", "pothole", pothole.id,
              old_value={"status": pothole.status.value}, new_value={"status": "VERIFIED"})
        return change_pothole_status(db, pothole, PotholeStatus.VERIFIED, user.name)
    if payload.action == "reject":
        audit(db, user.id, user.name, "pothole_rejected", "pothole", pothole.id,
              old_value={"status": pothole.status.value}, new_value={"status": "REJECTED"})
        return change_pothole_status(db, pothole, PotholeStatus.REJECTED, user.name, payload.reason or "")
    raise bad_request("action must be 'verify' or 'reject'")


@router.post("/{pothole_id}/assign", response_model=PotholeOut)
def assign(
    pothole_id: str,
    payload: AssignRequest,
    user: User = Depends(require_government),
    db: Session = Depends(get_db),
):
    pothole = _get_or_404(db, pothole_id)
    deadline = None
    if payload.deadline:
        try:
            deadline = datetime.fromisoformat(payload.deadline.replace("Z", "+00:00"))
        except ValueError:
            raise bad_request("Invalid deadline format")
    else:
        deadline = datetime.utcnow() + timedelta(days=payload.deadline_days)
    repair = assign_team(db, pothole, payload.team_id, deadline)
    audit(db, user.id, user.name, "repair_assigned", "repair", repair.id,
          old_value={"status": pothole.status.value}, new_value={"team_id": payload.team_id})
    db.refresh(pothole)
    return pothole


@router.patch("/{pothole_id}/status", response_model=PotholeOut)
def update_status(
    pothole_id: str,
    payload: UpdateStatusRequest,
    user: User = Depends(require_government),
    db: Session = Depends(get_db),
):
    pothole = _get_or_404(db, pothole_id)
    old = pothole.status.value
    result = change_pothole_status(db, pothole, payload.status, user.name, payload.note or "")
    audit(db, user.id, user.name, "status_changed", "pothole", pothole.id,
          old_value={"status": old}, new_value={"status": result.status.value})
    return result


@router.post("/{pothole_id}/prioritize", response_model=PotholeOut)
def override_priority(
    pothole_id: str,
    payload: OverridePriorityRequest,
    user: User = Depends(require_government),
    db: Session = Depends(get_db),
):
    pothole = _get_or_404(db, pothole_id)
    old = pothole.priority.value
    pothole.priority = payload.priority
    pothole.priority_score = payload.priority_score if payload.priority_score is not None else {
        Priority.CRITICAL: 90, Priority.HIGH: 70, Priority.MEDIUM: 50, Priority.LOW: 20
    }[payload.priority]
    pothole.priority_override_reason = payload.reason
    pothole.priority_modified_by = user.name
    pothole.priority_modified_at = datetime.utcnow()
    db.commit()
    db.refresh(pothole)
    audit(db, user.id, user.name, "priority_override", "pothole", pothole.id,
          old_value={"priority": old}, new_value={"priority": payload.priority.value})
    return pothole


@router.post("/recompute-priorities", response_model=int, include_in_schema=False)
def recompute_priorities(db: Session = Depends(get_db),
                         _: User = Depends(require_government)):
    potholes = db.query(Pothole).filter(
        Pothole.status.in_([PotholeStatus.PENDING_VERIFICATION, PotholeStatus.VERIFIED,
                            PotholeStatus.PRIORITIZED, PotholeStatus.ASSIGNED,
                            PotholeStatus.IN_PROGRESS])
    ).all()
    for p in potholes:
        if p.priority_modified_by:
            continue  # respect manual override
        days = pending_days_since(p.created_at)
        result = compute_priority(
            severity_score=p.severity_score,
            supporting_reports=p.report_count,
            pending_days=days,
        )
        p.priority_score = result["score"]
        p.priority = result["priority"]
    db.commit()
    return len(potholes)


@router.get("/nearby", response_model=list[PotholeOut], include_in_schema=False)
def nearby(lat: float, lon: float, radius_km: float = 1.0, db: Session = Depends(get_db)):
    from app.ai.cv.area_estimator import haversine_km

    potholes = db.query(Pothole).all()
    result = [p for p in potholes if haversine_km(lat, lon, p.latitude, p.longitude) <= radius_km]
    return sorted(result, key=lambda p: haversine_km(lat, lon, p.latitude, p.longitude))
