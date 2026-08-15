"""In-app notifications."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Notification, User

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def my_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread = db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read == False  # noqa: E712
    ).count()
    return {
        "unread": unread,
        "items": [
            {
                "id": n.id, "type": n.type.value, "title": n.title, "message": n.message,
                "link": n.link, "is_read": n.is_read, "created_at": n.created_at,
                "pothole_id": n.pothole_id,
            }
            for n in items
        ],
    }


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    item = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == user.id
    ).first()
    if item:
        item.is_read = True
        db.commit()
    return {"ok": True}


@router.post("/read-all")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id).update(
        {"is_read": True}, synchronize_session=False
    )
    db.commit()
    return {"ok": True}
