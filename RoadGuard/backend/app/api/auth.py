"""Authentication endpoints."""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.enums import Role
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import (
    PasswordChange,
    TokenOut,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
)
from app.utils.errors import bad_request, unauthorized

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise bad_request("An account with this email already exists")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=Role.CITIZEN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role.value)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise unauthorized("Invalid email or password")
    if not user.is_active:
        raise unauthorized("Account is deactivated")
    token = create_access_token(user.id, user.role.value)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login-form", response_model=TokenOut, include_in_schema=False)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise unauthorized("Invalid email or password")
    token = create_access_token(user.id, user.role.value)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.name:
        user.name = payload.name
    if payload.phone is not None:
        user.phone = payload.phone
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/password")
def change_password(
    payload: PasswordChange,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.hashed_password):
        raise bad_request("Current password is incorrect")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"ok": True}


@router.post("/demo-login", response_model=TokenOut, include_in_schema=False)
def demo_login(db: Session = Depends(get_db)):
    """Convenience endpoint for demo mode: returns tokens for each demo role."""
    rows = db.query(User).filter(User.role.in_([Role.CITIZEN, Role.GOVERNMENT_OFFICIAL,
                                               Role.ADMIN, Role.REPAIR_TEAM])).all()
    if not rows:
        raise bad_request("No demo users found. Run the seed script first.")
    users = [UserOut.model_validate(u).model_dump() for u in rows]
    return {"access_token": create_access_token(rows[0].id, rows[0].role.value),
            "token_type": "bearer", "user": users[0], "demo_users": users}


@router.get("/roles", response_model=list[str], include_in_schema=False)
def list_roles(user: User = Depends(require_admin)):
    return [r.value for r in Role]
