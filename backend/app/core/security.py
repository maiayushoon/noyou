"""Password hashing (bcrypt) and JWT access tokens.

Uses the ``bcrypt`` library directly rather than passlib to avoid version-coupling
warnings, and PyJWT for tokens. bcrypt's 72-byte input limit is handled explicitly.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings

_BCRYPT_MAX_BYTES = 72


def _truncate(password: str) -> bytes:
    """bcrypt silently ignores bytes past 72; truncate deterministically."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_truncate(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire, "iat": now, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None


# --- OAuth CSRF state tokens -------------------------------------------------
# The OAuth ``state`` parameter is a short-TTL, HMAC-signed JWT. The signature
# binds the caller's identity, the target provider, and (for PKCE) the code
# verifier, so a forged or replayed callback fails verification. No server-side
# session store is needed: everything the callback needs travels inside the
# signed token. These reuse the project's existing HS256/SECRET_KEY JWT stack.

_OAUTH_STATE_TYP = "oauth_state"


def create_state_token(payload: dict, ttl_seconds: int = 600) -> str:
    """Sign an OAuth ``state`` payload into a short-lived JWT.

    Adds a random ``nonce`` (CSRF), a ``typ`` of ``oauth_state``, and ``exp``/``iat``.
    Never put secrets that must stay confidential in here — it is signed, not
    encrypted (PKCE verifiers are fine: they are single-use, short-lived, and the
    signature prevents tampering).
    """
    now = datetime.now(timezone.utc)
    claims = dict(payload)
    claims.update(
        {
            "typ": _OAUTH_STATE_TYP,
            "nonce": secrets.token_urlsafe(16),
            "iat": now,
            "exp": now + timedelta(seconds=ttl_seconds),
        }
    )
    return jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)


def verify_state_token(token: str) -> dict | None:
    """Decode + validate an OAuth ``state`` token.

    Returns the original payload (claims) on success, or ``None`` if the token is
    expired, tampered, or not of ``typ=oauth_state``. Enforcing ``exp`` and ``typ``
    here defeats CSRF, replay, and cross-token confusion.
    """
    try:
        claims = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
    if claims.get("typ") != _OAUTH_STATE_TYP:
        return None
    return claims
