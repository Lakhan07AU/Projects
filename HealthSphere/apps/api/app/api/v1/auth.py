from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import audit, get_current_user
from app.core.errors import AppError, PermissionDeniedError
from app.core.rate_limit import rate_limit
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import RefreshSession, User
from app.schemas.schemas import LoginIn, RefreshIn, RegisterIn, TokenPair, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(db: Session, user: User) -> TokenPair:
    access = create_access_token(user.id)
    refresh, jti = create_refresh_token(user.id)
    db.add(
        RefreshSession(
            user_id=user.id,
            jti=jti,
            expires_at=datetime.now(timezone.utc) + timedelta(days=14),
        )
    )
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=TokenPair, status_code=201)
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)):
    rate_limit(f"register:{request.client.host if request.client else ''}", 10, 3600)

    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise AppError("EMAIL_TAKEN", "An account with this email already exists.", 409)

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
    )
    db.add(user)
    db.commit()
    audit(request, db, user.id, "REGISTER")
    return _issue_tokens(db, user)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    rate_limit(f"login:{request.client.host if request.client else ''}", 20, 900)

    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise PermissionDeniedError("Incorrect email or password")
    if not user.is_active or user.is_deleted():
        raise PermissionDeniedError("Account is not available")

    audit(request, db, user.id, "LOGIN")
    return _issue_tokens(db, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, request: Request, db: Session = Depends(get_db)):
    rate_limit(f"refresh:{request.client.host if request.client else ''}", 60, 900)
    try:
        claims = decode_token(payload.refresh_token)
    except Exception:
        raise PermissionDeniedError("Invalid refresh token")

    if claims.get("type") != "refresh":
        raise PermissionDeniedError("Invalid refresh token")

    session = (
        db.query(RefreshSession).filter(RefreshSession.jti == claims["jti"]).first()
    )
    if session is None or session.revoked_at is not None or session.expires_at.replace(
        tzinfo=timezone.utc
    ) < datetime.now(timezone.utc):
        raise PermissionDeniedError("Session has been revoked. Please log in again.")

    user = db.get(User, int(claims["sub"]))
    if not user or not user.is_active or user.is_deleted():
        raise PermissionDeniedError("Account is not available")

    # Rotate: revoke old session, issue a new pair
    session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return _issue_tokens(db, user)


@router.post("/logout")
def logout(
    request: Request,
    payload: RefreshIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        claims = decode_token(payload.refresh_token)
        if int(claims.get("sub", -1)) != user.id:
            raise PermissionDeniedError("Token does not belong to this account")
        session = (
            db.query(RefreshSession).filter(RefreshSession.jti == claims["jti"]).first()
        )
        if session:
            session.revoked_at = datetime.now(timezone.utc)
            db.commit()
    except PermissionDeniedError:
        raise
    except Exception:
        pass  # logout is best-effort for malformed tokens
    audit(request, db, user.id, "LOGOUT")
    return {"success": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
