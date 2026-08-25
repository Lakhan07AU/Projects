"""FastAPI dependencies: current user resolution and audit helper."""
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt as pyjwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import PermissionDeniedError
from app.core.security import decode_token
from app.models import AuditLog, User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise PermissionDeniedError("Authentication required")
    try:
        payload = decode_token(credentials.credentials)
    except pyjwt.ExpiredSignatureError:
        raise PermissionDeniedError("Token has expired")
    except pyjwt.PyJWTError:
        raise PermissionDeniedError("Invalid authentication token")

    if payload.get("type") != "access":
        raise PermissionDeniedError("Invalid authentication token")

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active or user.is_deleted():
        raise PermissionDeniedError("Account is not available")
    return user


def audit(
    request: Request,
    db: Session,
    user_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    """Record an audit event. Metadata must never include medical content."""
    client_ip = None
    if request.client:
        client_ip = request.client.host
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata or {},
            ip_address=client_ip,
        )
    )
    db.commit()
