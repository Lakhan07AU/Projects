"""Password hashing (bcrypt) and JWT creation/verification."""
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt as pyjwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, token_type: str, expires_delta: timedelta, extra: dict | None = None) -> tuple[str, str]:
    jti = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti,
    }
    if extra:
        payload.update(extra)
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM), jti


def create_access_token(user_id: int) -> str:
    token, _ = _create_token(
        str(user_id), "access", timedelta(minutes=settings.access_token_expire_minutes)
    )
    return token


def create_refresh_token(user_id: int) -> tuple[str, str]:
    """Returns (token, jti) — the jti is stored server-side for revocation."""
    return _create_token(
        str(user_id), "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> dict:
    return pyjwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
