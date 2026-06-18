"""Public account-lifecycle routes: email verification and password reset.

These complement ``auth.py`` (register / login). They are deliberately written to
avoid *account enumeration*: the resend-verification and forgot-password endpoints
always return the same 200 response whether or not the email belongs to a real,
eligible account, so an attacker cannot probe which addresses are registered.

The router uses the same ``prefix="/auth"`` as ``auth.py`` and must be included
AFTER ``auth.router`` in ``api/router.py``.

NOTE: no ``from __future__ import annotations`` here — slowapi's @limiter.limit
wrapper breaks FastAPI's resolution of deferred (string) annotations such as
``request: Request``; real annotation objects avoid that.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.ratelimit import AUTH_LIMIT, limiter
from ...core.security import hash_password
from ...models.user import User
from ...schemas.auth_extra import (
    EmailRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenRequest,
)
from ...services.account_email import (
    PURPOSE_RESET,
    PURPOSE_VERIFY,
    consume_token,
    send_password_reset,
    send_verification,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Identical copy reused for both enumeration-safe endpoints.
_GENERIC_OK = "If an account exists for that address, an email has been sent."


@router.post("/resend-verification", response_model=MessageResponse)
@limiter.limit(AUTH_LIMIT)
def resend_verification(request: Request, payload: EmailRequest, db: Session = Depends(get_db)):
    """Re-send the verification email.

    Always returns 200 with a generic message. A verification email is only
    actually dispatched when the account exists and is not yet verified.
    """
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is not None and not user.is_verified:
        send_verification(db, user)
    return MessageResponse(message=_GENERIC_OK)


@router.post("/verify-email", response_model=MessageResponse)
@limiter.limit(AUTH_LIMIT)
def verify_email(request: Request, payload: TokenRequest, db: Session = Depends(get_db)):
    """Confirm an email address from a verification token.

    POST is used (rather than a GET link target) so the secret token travels in
    the request body instead of being logged in server access logs / referrers.
    """
    user = consume_token(db, payload.token, PURPOSE_VERIFY)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link.",
        )
    user.is_verified = True
    db.add(user)
    db.commit()
    return MessageResponse(message="Your email address has been verified.")


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit(AUTH_LIMIT)
def forgot_password(request: Request, payload: EmailRequest, db: Session = Depends(get_db)):
    """Begin a password reset.

    Always returns 200 with a generic message. ``send_password_reset`` is a no-op
    when no account matches, so this endpoint cannot be used to enumerate users.
    """
    user = db.scalar(select(User).where(User.email == payload.email))
    send_password_reset(db, user)
    return MessageResponse(message=_GENERIC_OK)


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit(AUTH_LIMIT)
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Complete a password reset using a reset token and a new password."""
    user = consume_token(db, payload.token, PURPOSE_RESET)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link.",
        )
    user.password_hash = hash_password(payload.new_password)
    # Invalidate any access tokens issued before now (revokes stolen sessions).
    user.password_changed_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    return MessageResponse(message="Your password has been reset. You can now sign in.")
