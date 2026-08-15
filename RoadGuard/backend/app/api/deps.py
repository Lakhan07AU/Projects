"""FastAPI dependencies: current user and role-based access control."""
from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.enums import Role
from app.core.security import decode_token
from app.db.database import get_db
from app.db.models import User
from app.utils.errors import forbidden, unauthorized

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
    except Exception as exc:  # noqa: BLE001
        raise unauthorized("Invalid or expired token") from exc
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise unauthorized("User not found or inactive")
    return user


def require_roles(*roles: Role):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise forbidden()
        return user

    return checker


def require_government(user: User = Depends(get_current_user)) -> User:
    if user.role not in (Role.GOVERNMENT_OFFICIAL, Role.ADMIN):
        raise forbidden("Only government officials or admins can perform this action")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.ADMIN:
        raise forbidden("Admin access required")
    return user
