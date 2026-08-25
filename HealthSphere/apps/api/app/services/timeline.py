"""Unified health timeline service."""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import HealthTimelineEvent, TimelineEventType


def add_event(
    db: Session,
    *,
    user_id: int,
    event_type: TimelineEventType,
    event_date: datetime | None = None,
    title: str,
    description: str | None = None,
    source: str = "system",
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
) -> HealthTimelineEvent:
    event = HealthTimelineEvent(
        user_id=user_id,
        event_type=event_type,
        event_date=event_date or datetime.now(),
        title=title[:255],
        description=description,
        source=source[:64],
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(event)
    return event
