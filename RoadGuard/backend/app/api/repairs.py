"""Repair endpoints: team + government."""
from __future__ import annotations

import io
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.ai.cv.segmenter import Segmenter
from app.api.deps import get_current_user, require_government
from app.core.enums import PotholeStatus, Role
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Pothole, Repair, RepairTeam, RepairUpdate, User
from app.schemas.repair import RepairOut, RepairWithPothole, RepairUpdateOut
from app.services.repair_workflow import complete_repair
from app.utils.errors import bad_request, forbidden, not_found
from app.utils.file_validation import validate_image

settings = get_settings()
router = APIRouter(prefix="/api/repairs", tags=["repairs"])


def _pothole_dict(p: Pothole) -> dict:
    return {
        "id": p.id,
        "pothole_code": p.pothole_code,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "road": p.road,
        "ward": p.ward,
        "city": p.city,
        "severity": p.severity.value,
        "severity_score": p.severity_score,
        "priority": p.priority.value,
        "priority_score": p.priority_score,
        "repair_area": p.repair_area,
        "estimated_cost": p.estimated_cost,
        "actual_cost": p.actual_cost,
        "status": p.status.value,
        "before_image": p.before_image,
        "after_image": p.after_image,
        "report_count": p.report_count,
    }


def _get_repair(db: Session, repair_id: str) -> Repair:
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise not_found("Repair not found")
    return repair


def _repair_out(r: Repair) -> RepairWithPothole:
    data = RepairOut.model_validate(r).model_dump()
    data["pothole"] = _pothole_dict(r.pothole) if r.pothole else None
    return RepairWithPothole(**data)


@router.get("", response_model=list[RepairWithPothole])
def list_repairs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: str | None = None,
):
    query = db.query(Repair)
    if user.role == Role.REPAIR_TEAM:
        team = db.query(RepairTeam).filter(RepairTeam.name == user.name).first()
        query = query.filter(Repair.team_id == team.id) if team else query.filter(Repair.team_id == -1)
    if status:
        query = query.filter(Repair.status == status.upper())
    repairs = query.order_by(Repair.created_at.desc()).all()
    return [_repair_out(r) for r in repairs]


@router.get("/{repair_id}", response_model=RepairWithPothole)
def get_repair(repair_id: str, user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise not_found("Repair not found")
    return _repair_out(repair)


@router.post("/{repair_id}/accept", response_model=RepairWithPothole)
def accept_repair(repair_id: str, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    repair = _get_repair(db, repair_id)
    if repair.status not in ("ASSIGNED", "SCHEDULED"):
        raise bad_request("Repair cannot be accepted in current status")
    repair.status = "ASSIGNED"
    repair.accepted_at = datetime.utcnow()
    db.add(RepairUpdate(repair_id=repair.id, status="ASSIGNED", note="Accepted by team", created_by=user.name))
    db.commit()
    db.refresh(repair)
    return _repair_out(repair)


@router.post("/{repair_id}/start", response_model=RepairWithPothole)
def start_repair(repair_id: str, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    repair = _get_repair(db, repair_id)
    if repair.status != "ASSIGNED":
        raise bad_request("Repair must be assigned before starting")
    repair.status = "IN_PROGRESS"
    repair.start_date = datetime.utcnow()
    repair.pothole.status = PotholeStatus.IN_PROGRESS
    db.add(RepairUpdate(repair_id=repair.id, status="IN_PROGRESS", note="Work started", created_by=user.name))
    db.commit()
    db.refresh(repair)
    return _repair_out(repair)


@router.post("/{repair_id}/progress", response_model=RepairUpdateOut)
def progress_update(
    repair_id: str,
    note: str = Form(""),
    file: UploadFile | None = File(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repair = _get_repair(db, repair_id)
    image_path = None
    if file is not None:
        content = validate_image(file)
        sub = settings.storage_path / "repairs"
        sub.mkdir(parents=True, exist_ok=True)
        name = f"{uuid.uuid4().hex}.jpg"
        (sub / name).write_bytes(content)
        image_path = f"/uploads/repairs/{name}"
    update = RepairUpdate(
        repair_id=repair.id,
        status=repair.status,
        note=note or "Progress update",
        image_path=image_path,
        created_by=user.name,
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


@router.post("/{repair_id}/complete", response_model=RepairWithPothole)
def complete(
    repair_id: str,
    actual_cost: float = Form(...),
    note: str = Form(""),
    file: UploadFile | None = File(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repair = _get_repair(db, repair_id)
    after_path = None
    if file is not None:
        content = validate_image(file)
        sub = settings.storage_path / "repairs"
        sub.mkdir(parents=True, exist_ok=True)
        name = f"{uuid.uuid4().hex}.jpg"
        (sub / name).write_bytes(content)
        after_path = f"/uploads/repairs/{name}"

    repair = complete_repair(
        db, repair.pothole, actual_cost, user.name, note
    )
    if after_path:
        repair.after_image = after_path
        repair.pothole.after_image = after_path
        db.commit()

    db.refresh(repair)
    return _repair_out(repair)


@router.post("/{repair_id}/verify", response_model=dict)
def ai_verify(
    repair_id: str,
    file: UploadFile = File(...),
    user: User = Depends(require_government),
    db: Session = Depends(get_db),
):
    """AI-assisted before/after repair verification.

    Compares the after image with the stored before image and produces a
    verification score. Clearly labelled as AI-assisted, not certification.
    """
    repair = _get_repair(db, repair_id)
    if not repair.pothole.before_image:
        raise bad_request("No before image available for comparison")

    content = validate_image(file)
    try:
        after_img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:  # noqa: BLE001
        raise bad_request("Could not open after image") from None

    try:
        before_img = Image.open(settings.storage_path / repair.pothole.before_image.replace("/uploads/", "")).convert("RGB")
    except Exception:  # noqa: BLE001
        before_img = after_img

    segmenter = Segmenter(demo=settings.DEMO_MODE)
    before_segs = segmenter.segment(before_img, [{"bbox": [0, 0, before_img.width, before_img.height]}])
    after_segs = segmenter.segment(after_img, [{"bbox": [0, 0, after_img.width, after_img.height]}])
    before_area = before_segs[0]["pixel_area"]
    after_area = after_segs[0]["pixel_area"]
    reduction = (before_area - after_area) / before_area * 100 if before_area else 0.0
    score = max(0.0, min(100.0, reduction))

    repair.verification_score = round(score, 1)
    repair.pothole.after_image = f"/uploads/repairs/{uuid.uuid4().hex}.jpg"
    db.commit()

    return {
        "verification_score": round(score, 1),
        "before_pixel_area": before_area,
        "after_pixel_area": after_area,
        "reduction_percent": round(max(0.0, reduction), 1),
        "label": "AI-assisted repair verification",
        "note": "Indicative result. Not an official engineering certification.",
    }
