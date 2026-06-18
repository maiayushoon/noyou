"""Account-email service: issue, send, and consume verification / reset tokens.

This sits between the auth routes and the persistence + notification layers:

* ``create_token``        -- mint and persist a single-use, expiring token.
* ``send_verification``   -- email a "confirm your address" link.
* ``send_password_reset`` -- email a "reset your password" link (no-op if the
                             account does not exist, to avoid account enumeration).
* ``consume_token``       -- validate and burn a token, returning its owner.

Tokens are opaque ``secrets.token_urlsafe`` values, so they are not guessable and
carry no PII. Expiry windows come from settings and differ by purpose.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.user import User
from ..models.verification_token import VerificationToken
from ..notifications.dispatcher import dispatch_alert
from .email_templates import password_reset_email, verification_email

# Recognized token purposes. Kept here so callers and the DB agree on the labels.
PURPOSE_VERIFY = "verify"
PURPOSE_RESET = "reset"
_PURPOSES = (PURPOSE_VERIFY, PURPOSE_RESET)

# token_urlsafe(32) yields ~43 chars, comfortably under the column's 64.
_TOKEN_BYTES = 32


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_token() -> str:
    """Return a cryptographically-strong, URL-safe token string."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def _expiry_for(purpose: str) -> datetime:
    """Compute the absolute expiry for a token of the given purpose."""
    if purpose == PURPOSE_RESET:
        hours = settings.reset_token_expire_hours
    else:
        hours = settings.email_token_expire_hours
    return _utcnow() + timedelta(hours=hours)


def create_token(db: Session, user: User, purpose: str) -> VerificationToken:
    """Mint, persist, and return a fresh token for ``user`` and ``purpose``.

    Raises ``ValueError`` on an unknown purpose so a programming mistake fails
    loudly rather than writing a meaningless row.
    """
    if purpose not in _PURPOSES:
        raise ValueError(f"Unknown token purpose: {purpose!r}")

    token = VerificationToken(
        user_id=user.id,
        token=generate_token(),
        purpose=purpose,
        expires_at=_expiry_for(purpose),
        used=False,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def send_verification(db: Session, user: User) -> VerificationToken:
    """Create a verification token and email the confirmation link to ``user``."""
    record = create_token(db, user, PURPOSE_VERIFY)
    verify_url = f"{settings.frontend_url}/verify?token={record.token}"
    subject, body = verification_email(user.full_name, verify_url)
    dispatch_alert(user.email, subject, body)
    return record


def send_password_reset(db: Session, user: User | None) -> VerificationToken | None:
    """Create a reset token and email the reset link.

    Accepts ``None`` (e.g. when no account matched the submitted email) and does
    nothing in that case, so the public endpoint cannot be used to enumerate which
    addresses are registered.
    """
    if user is None:
        return None
    record = create_token(db, user, PURPOSE_RESET)
    reset_url = f"{settings.frontend_url}/reset?token={record.token}"
    subject, body = password_reset_email(user.full_name, reset_url)
    dispatch_alert(user.email, subject, body)
    return record


def consume_token(db: Session, token: str, purpose: str) -> User | None:
    """Validate and single-use-consume a token, returning its owning user.

    Returns ``None`` (rather than raising) for every failure mode -- missing,
    wrong purpose, already used, or expired -- so callers can surface one generic
    error and not leak which check failed. On success the token is marked ``used``
    and committed before returning.
    """
    if not token or purpose not in _PURPOSES:
        return None

    record = db.scalar(select(VerificationToken).where(VerificationToken.token == token))
    if record is None:
        return None
    if record.purpose != purpose or record.used:
        return None

    # Normalize to an aware datetime: SQLite may hand back a naive value even
    # though it was stored with tz info.
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= _utcnow():
        return None

    user = db.get(User, record.user_id)
    if user is None:
        return None

    record.used = True
    db.add(record)
    db.commit()
    return user
