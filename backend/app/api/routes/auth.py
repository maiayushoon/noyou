# NOTE: deliberately no `from __future__ import annotations` here — slowapi's
# @limiter.limit wrapper breaks FastAPI's resolution of string (deferred)
# annotations like `request: Request`. Real annotation objects avoid that.
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.database import get_db
from ...core.ratelimit import AUTH_LIMIT, limiter
from ...core.security import create_access_token, hash_password, verify_password
from ...models.user import User
from ...schemas.auth import Token, UserLogin, UserOut, UserRegister
from ...services.account_email import send_verification
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

_UNVERIFIED_DETAIL = "Email not verified. Please check your inbox for the verification link."


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_LIMIT)
def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if settings.require_email_verification:
        # Account starts unverified (column default); email the confirmation link.
        send_verification(db, user)
    else:
        # Verification disabled — mark verified so login() never blocks these users.
        user.is_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.post("/login", response_model=Token)
@limiter.limit(AUTH_LIMIT)
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if settings.require_email_verification and not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_UNVERIFIED_DETAIL)
    return Token(access_token=create_access_token(str(user.id)))


@router.post("/token", response_model=Token, include_in_schema=False)
def login_oauth(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 password-flow endpoint so Swagger's Authorize button works.

    Covered by the global default rate limit. (The per-route AUTH_LIMIT decorator is
    omitted here: slowapi's wrapper conflicts with FastAPI resolving the
    OAuth2PasswordRequestForm forward-ref under ``from __future__ import annotations``.)
    """
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if settings.require_email_verification and not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_UNVERIFIED_DETAIL)
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
