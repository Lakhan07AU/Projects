"""In-app notification service."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import NotifType
from app.db.models import Notification


def notify(
    db: Session,
    user_id: str,
    title: str,
    message: str = "",
    link: str = "",
    ntype: NotifType = NotifType.SYSTEM,
    pothole_id: str | None = None,
) -> Notification:
    item = Notification(
        user_id=user_id,
        title=title,
        message=message,
        link=link,
        type=ntype,
        pothole_id=pothole_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
