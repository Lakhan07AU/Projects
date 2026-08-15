"""Repair workflow: validates status transitions and tracks change history."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.enums import PotholeStatus, STATUS_TRANSITIONS
from app.db.models import Pothole, Repair, RepairUpdate, RepairTeam
from app.utils.errors import bad_request, not_found


def _repair_for_pothole(db: Session, pothole_id: str) -> Repair:
    repair = db.query(Repair).filter(Repair.pothole_id == pothole_id).first()
    if not repair:
        raise not_found("Repair not found for this pothole")
    return repair


def change_pothole_status(
    db: Session,
    pothole: Pothole,
    new_status: PotholeStatus,
    actor: str | None = None,
    note: str = "",
) -> Pothole:
    current = pothole.status
    allowed = STATUS_TRANSITIONS.get(current, set())
    if new_status not in allowed:
        raise bad_request(
            f"Invalid transition: {current.value} -> {new_status.value}. "
            f"Allowed: {sorted(s.value for s in allowed) or 'none'}"
        )

    pothole.status = new_status
    if new_status == PotholeStatus.REJECTED:
        pothole.rejected_reason = note or None

    repair = db.query(Repair).filter(Repair.pothole_id == pothole.id).first()
    if repair:
        repair.status = _map_pothole_to_repair_status(new_status)
        if new_status == PotholeStatus.IN_PROGRESS and not repair.start_date:
            repair.start_date = datetime.utcnow()
        if new_status == PotholeStatus.COMPLETED:
            repair.completion_date = repair.completion_date or datetime.utcnow()
        db.add(RepairUpdate(
            repair_id=repair.id,
            status=repair.status,
            note=note or f"Status -> {new_status.value}",
            created_by=actor,
        ))

    db.add(pothole)
    db.commit()
    db.refresh(pothole)
    return pothole


def _map_pothole_to_repair_status(status: PotholeStatus) -> str:
    mapping = {
        PotholeStatus.SUBMITTED: "SCHEDULED",
        PotholeStatus.AI_ANALYZED: "SCHEDULED",
        PotholeStatus.PENDING_VERIFICATION: "SCHEDULED",
        PotholeStatus.VERIFIED: "SCHEDULED",
        PotholeStatus.PRIORITIZED: "SCHEDULED",
        PotholeStatus.ASSIGNED: "ASSIGNED",
        PotholeStatus.IN_PROGRESS: "IN_PROGRESS",
        PotholeStatus.COMPLETED: "COMPLETED",
        PotholeStatus.CITIZEN_VERIFICATION: "COMPLETED",
        PotholeStatus.CLOSED: "CLOSED",
    }
    return mapping.get(status, "SCHEDULED")


def assign_team(
    db: Session,
    pothole: Pothole,
    team_id: int,
    deadline: datetime | None = None,
) -> Repair:
    team = db.query(RepairTeam).filter(RepairTeam.id == team_id).first()
    if not team:
        raise not_found("Repair team not found")

    repair = db.query(Repair).filter(Repair.pothole_id == pothole.id).first()
    if not repair:
        repair = Repair(
            pothole_id=pothole.id,
            estimated_cost=pothole.estimated_cost,
            repair_area=pothole.repair_area,
            status="ASSIGNED",
            assigned_at=datetime.utcnow(),
            deadline=deadline,
        )
        db.add(repair)
        db.flush()
    repair.team_id = team_id
    repair.status = "ASSIGNED"
    repair.assigned_at = datetime.utcnow()
    if deadline:
        repair.deadline = deadline

    pothole.status = PotholeStatus.ASSIGNED
    db.add(RepairUpdate(
        repair_id=repair.id,
        status="ASSIGNED",
        note=f"Assigned to team {team.name}",
    ))
    db.commit()
    db.refresh(repair)
    return repair


def complete_repair(
    db: Session,
    pothole: Pothole,
    actual_cost: float,
    actor: str | None = None,
    note: str = "",
) -> Repair:
    repair = _repair_for_pothole(db, pothole.id)
    if repair.status not in ("IN_PROGRESS", "ASSIGNED"):
        raise bad_request(f"Cannot complete repair in status '{repair.status}'")
    repair.actual_cost = actual_cost
    repair.status = "COMPLETED"
    repair.completion_date = datetime.utcnow()
    pothole.actual_cost = actual_cost
    pothole.status = PotholeStatus.COMPLETED
    db.add(RepairUpdate(
        repair_id=repair.id,
        status="COMPLETED",
        note=note or "Repair marked completed by team",
        cost=actual_cost,
        created_by=actor,
    ))
    db.commit()
    db.refresh(repair)
    return repair
