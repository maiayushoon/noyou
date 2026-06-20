"""Centralized access-token validity + refresh for linked accounts.

Both the owned-content connector and the scheduler obtain a usable access token
through :func:`get_valid_token`, so refresh logic lives in exactly one place.

Flow:
  1. Decrypt the stored access token.
  2. If it expires within a small skew AND a refresh token exists, call the
     provider's ``refresh`` and persist the re-encrypted new access/refresh/expiry.
  3. If the token is expired with no usable refresh (or refresh fails), mark the
     row ``status="expired"`` and raise :class:`TokenExpired` so callers no-op.

Mastodon tokens don't expire, so refresh is skipped (``token_expires_at`` is NULL).
Never logs tokens or ciphertext.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ...core.crypto import decrypt_token, encrypt_token
from ...models.linked_account import LinkedAccount
from . import get_provider

# Refresh slightly before actual expiry to avoid races at the boundary.
_SKEW_SECONDS = 60


class TokenExpired(Exception):
    """Raised when a linked account has no usable (and unrefreshable) token."""


def _is_expired(linked: LinkedAccount, *, skew: int = _SKEW_SECONDS) -> bool:
    if linked.token_expires_at is None:
        return False
    expires = linked.token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= (expires - timedelta(seconds=skew))


def get_valid_token(db: Session, linked: LinkedAccount) -> str:
    """Return a usable plaintext access token for ``linked``, refreshing if needed.

    Raises :class:`TokenExpired` (after marking ``status="expired"``) when no valid
    token can be produced. The plaintext is only held in memory by the caller for
    the duration of a single API call — never persisted or logged.
    """
    access = decrypt_token(linked.access_token_enc)

    if not _is_expired(linked):
        if access:
            return access
        # Ciphertext unreadable (e.g. SECRET_KEY rotated) — treat as expired.
        _mark_expired(db, linked, "token unreadable; re-link required")
        raise TokenExpired(f"linked_account {linked.id}: token unreadable")

    # Token is at/near expiry — try to refresh.
    provider = get_provider(linked.provider)
    refresh_plain = decrypt_token(linked.refresh_token_enc) if linked.refresh_token_enc else ""
    if provider is None or not refresh_plain:
        _mark_expired(db, linked, "token expired; no refresh available")
        raise TokenExpired(f"linked_account {linked.id}: expired, no refresh")

    bundle = provider.refresh(
        refresh_token=refresh_plain,
        access_token=access,
        instance_url=linked.instance_url,
    )
    if bundle is None or not bundle.access_token:
        _mark_expired(db, linked, "token refresh failed")
        raise TokenExpired(f"linked_account {linked.id}: refresh failed")

    # Persist the refreshed credentials (re-encrypted).
    linked.access_token_enc = encrypt_token(bundle.access_token)
    if bundle.refresh_token:
        linked.refresh_token_enc = encrypt_token(bundle.refresh_token)
    linked.token_expires_at = bundle.expires_at()
    if bundle.scopes:
        linked.scopes = bundle.scopes
    linked.status = "connected"
    linked.last_error = None
    db.add(linked)
    db.commit()
    return bundle.access_token


def _mark_expired(db: Session, linked: LinkedAccount, reason: str) -> None:
    linked.status = "expired"
    linked.last_error = reason[:500]
    db.add(linked)
    db.commit()
