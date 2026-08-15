"""Cost rate administration (admin only) and repair teams management."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin, require_government
from app.db.database import get_db
from app.db.models import CostRate, RepairTeam, User
from app.utils.errors import not_found

router = APIRouter(prefix="/api", tags=["admin"])


class RateUpdate(BaseModel):
    value: float


class RateCreate(RateUpdate):
    rate_key: str
    name: str
    unit: str = "INR"
    description: str = ""


class TeamCreate(BaseModel):
    name: str
    contact: str = ""
    manager_name: str = ""
    city: str = ""
    ward: str = ""


# ---------------- Cost rates ----------------

@router.get("/cost-rates")
def list_rates(db: Session = Depends(get_db), _: User = Depends(require_government)):
    rates = db.query(CostRate).order_by(CostRate.rate_key).all()
    return [
        {
            "id": r.id, "rate_key": r.rate_key, "name": r.name, "unit": r.unit,
            "value": r.value, "description": r.description,
            "previous_value": r.previous_value, "effective_date": r.effective_date,
            "updated_by": r.updated_by, "created_at": r.created_at,
        }
        for r in rates
    ]


@router.post("/cost-rates", status_code=201)
def create_rate(payload: RateCreate, user: User = Depends(require_admin),
                db: Session = Depends(get_db)):
    rate = CostRate(
        rate_key=payload.rate_key, name=payload.name, unit=payload.unit,
        value=payload.value, description=payload.description,
        effective_date=datetime.utcnow(), updated_by=user.name,
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


@router.patch("/cost-rates/{rate_id}")
def update_rate(rate_id: int, payload: RateUpdate, user: User = Depends(require_admin),
                db: Session = Depends(get_db)):
    rate = db.query(CostRate).filter(CostRate.id == rate_id).first()
    if not rate:
        raise not_found("Rate not found")
    rate.previous_value = rate.value
    rate.value = payload.value
    rate.effective_date = datetime.utcnow()
    rate.updated_by = user.name
    db.commit()
    db.refresh(rate)
    return rate


# ---------------- Repair teams ----------------

@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return [
        {
            "id": u.id, "name": u.name, "email": u.email, "phone": u.phone,
            "role": u.role.value, "is_active": u.is_active, "created_at": u.created_at,
        }
        for u in db.query(User).order_by(User.created_at.desc()).all()
    ]


@router.get("/teams")
def list_teams(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(RepairTeam).order_by(RepairTeam.name).all()


@router.post("/teams", status_code=201)
def create_team(payload: TeamCreate, user: User = Depends(require_admin),
                db: Session = Depends(get_db)):
    team = RepairTeam(**payload.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team
