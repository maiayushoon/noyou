"""Symmetric encryption for at-rest OAuth tokens.

Linked-account access/refresh tokens are stored ENCRYPTED (the ``*_enc`` columns
on :class:`~app.models.linked_account.LinkedAccount`); plaintext never touches the
database or the logs. We use Fernet (AES-128-CBC + HMAC, from ``cryptography``).

The Fernet key is derived **deterministically** from the existing ``SECRET_KEY`` so
no new secret is required to run the product: ``sha256(secret_key)`` yields 32 bytes,
url-safe-base64-encoded into a valid Fernet key. Because ``config.py`` already
refuses to boot outside development with a weak/short ``SECRET_KEY``, the derived
key is guaranteed strong in production.

An explicit ``TOKEN_ENCRYPTION_KEY`` (a urlsafe-base64 32-byte Fernet key) may be
set to decouple token encryption from ``SECRET_KEY`` (e.g. for key rotation). When
set it takes precedence over the derived key.

Caveat: rotating ``SECRET_KEY`` without a pinned ``TOKEN_ENCRYPTION_KEY``
invalidates every stored token, so users must re-link their accounts — the same
"tokens reset on restart in dev" trade-off the app already documents.
"""
from __future__ import annotations

import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from .config import settings


def _derive_key() -> bytes:
    """Return a valid Fernet key (urlsafe-base64 of 32 bytes).

    Prefers an explicit ``TOKEN_ENCRYPTION_KEY`` override; otherwise derives one
    deterministically from ``SECRET_KEY`` via SHA-256.
    """
    override = (settings.token_encryption_key or "").strip()
    if override:
        # Accept a ready-made Fernet key as-is. If a raw/arbitrary string was
        # supplied, fold it through sha256 so it still produces a valid 32-byte key.
        try:
            Fernet(override.encode("utf-8"))
            return override.encode("utf-8")
        except (ValueError, TypeError):
            digest = hashlib.sha256(override.encode("utf-8")).digest()
            return base64.urlsafe_b64encode(digest)
    digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    return Fernet(_derive_key())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token string, returning urlsafe-base64 ciphertext (str)."""
    if plaintext is None:
        plaintext = ""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_token(ciphertext: str) -> str:
    """Decrypt ciphertext produced by :func:`encrypt_token`.

    Returns ``""`` if the input is empty or cannot be decrypted (e.g. the key
    changed), so callers degrade to a no-op instead of raising.
    """
    if not ciphertext:
        return ""
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        return ""
