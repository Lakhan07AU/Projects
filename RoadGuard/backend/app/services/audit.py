"""Audit logging for government/admin actions."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditLog


def audit(
    db: Session,
    user_id: str | None,
    user_name: str,
    action: str,
    object_type: str = "",
    object_id: str = "",
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    ip: str = "",
) -> None:
    db.add(AuditLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        object_type=object_type,
        object_id=object_id,
        old_value=old_value,
        new_value=new_value,
        ip=ip,
    ))
    db.commit()
