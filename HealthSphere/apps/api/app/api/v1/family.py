"""Family health history: members, conditions, tree."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import NotFoundError
from app.models import FamilyCondition, FamilyMember, User
from app.schemas.schemas import FamilyConditionIn, FamilyConditionOut, FamilyMemberIn, FamilyMemberOut

router = APIRouter(prefix="/family", tags=["family"])


@router.get("/members", response_model=list[FamilyMemberOut])
def list_members(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(FamilyMember)
        .filter(FamilyMember.user_id == user.id)
        .order_by(FamilyMember.created_at)
        .all()
    )


@router.post("/members", response_model=FamilyMemberOut, status_code=201)
def add_member(
    payload: FamilyMemberIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = FamilyMember(user_id=user.id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)

    from app.services.timeline import add_event
    from app.models import TimelineEventType

    add_event(
        db,
        user_id=user.id,
        event_type=TimelineEventType.family_history,
        title=f"Family member added: {member.name} ({member.relationship})",
        source="user",
    )
    db.commit()
    audit(request, db, user.id, "FAMILY_MEMBER_ADDED", "family_member", member.id)
    return member


@router.put("/members/{member_id}", response_model=FamilyMemberOut)
def update_member(
    member_id: int,
    payload: FamilyMemberIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _owned_member(db, user.id, member_id)
    for field, value in payload.model_dump().items():
        setattr(member, field, value)
    db.commit()
    audit(request, db, user.id, "FAMILY_MEMBER_UPDATED", "family_member", member_id)
    return member


@router.delete("/members/{member_id}", status_code=204)
def delete_member(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _owned_member(db, user.id, member_id)
    db.delete(member)
    db.commit()
    audit(request, db, user.id, "FAMILY_MEMBER_DELETED", "family_member", member_id)


# ---- Conditions per member ----
@router.post("/members/{member_id}/conditions", response_model=FamilyConditionOut, status_code=201)
def add_family_condition(
    member_id: int,
    payload: FamilyConditionIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _owned_member(db, user.id, member_id)
    row = FamilyCondition(member_id=member.id, **payload.model_dump())
    db.add(row)
    db.commit()

    from app.services.timeline import add_event
    from app.models import TimelineEventType

    add_event(
        db,
        user_id=user.id,
        event_type=TimelineEventType.family_history,
        title=f"{member.name}: condition recorded — {row.condition_name}",
        source="user",
        related_entity_type="family_member",
        related_entity_id=member.id,
    )
    db.commit()
    audit(request, db, user.id, "FAMILY_CONDITION_ADDED", "family_condition", row.id)
    return row


@router.delete("/conditions/{condition_row_id}", status_code=204)
def delete_family_condition(
    condition_row_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = (
        db.query(FamilyCondition)
        .join(FamilyMember, FamilyCondition.member_id == FamilyMember.id)
        .filter(FamilyCondition.id == condition_row_id, FamilyMember.user_id == user.id)
        .first()
    )
    if not row:
        raise NotFoundError("Family condition not found")
    db.delete(row)
    db.commit()
    audit(request, db, user.id, "FAMILY_CONDITION_DELETED", "family_condition", condition_row_id)


@router.get("/summary")
def family_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aggregated (privacy-safe) view of the user's own family health patterns."""
    rows = (
        db.query(FamilyCondition.condition_name, FamilyMember.relationship)
        .join(FamilyMember, FamilyCondition.member_id == FamilyMember.id)
        .filter(FamilyMember.user_id == user.id)
        .all()
    )
    by_condition: dict[str, list[str]] = {}
    for name, rel in rows:
        key = name.strip().lower()
        by_condition.setdefault(key, []).append(rel)

    patterns = [
        {
            "condition": cond.title(),
            "occurrences": sorted(set(rels)),
            "note": (
                "Reported in more than one close relative — may be worth mentioning "
                "during preventive-care discussions."
                if len(set(rels)) > 1
                else "Recorded for one family member."
            ),
        }
        for cond, rels in sorted(by_condition.items(), key=lambda kv: -len(kv[1]))
    ]
    return {"total_members": db.query(FamilyMember).filter(FamilyMember.user_id == user.id).count(),
            "patterns": patterns}


def _owned_member(db: Session, user_id: int, member_id: int) -> FamilyMember:
    member = db.get(FamilyMember, member_id)
    if not member or member.user_id != user_id:
        raise NotFoundError("Family member not found")
    return member
