"""Plain-text email copy for account lifecycle messages.

Pure functions: given a recipient name and an action URL, return a
``(subject, body)`` tuple. No I/O, no settings access — easy to unit-test and to
swap for HTML templates later. Copy is intentionally ASCII-only to dodge SMTP /
terminal encoding issues.
"""
from __future__ import annotations

_BRAND = "NoYou"
_SIGNOFF = f"-- The {_BRAND} Team"


def _greeting(name: str | None) -> str:
    """Personalized greeting that degrades gracefully when no name is on file."""
    who = (name or "").strip()
    return f"Hi {who}," if who else "Hi,"


def verification_email(name: str | None, verify_url: str) -> tuple[str, str]:
    """Email asking a new user to confirm their address."""
    subject = f"Confirm your {_BRAND} email address"
    body = (
        f"{_greeting(name)}\n\n"
        f"Welcome to {_BRAND} -- your AI digital-reputation co-pilot.\n\n"
        "Please confirm your email address to activate your account by visiting "
        "the link below:\n\n"
        f"{verify_url}\n\n"
        "If the link does not open, copy and paste the full address into your "
        "browser.\n\n"
        "This link will expire for your security. If you did not create a "
        f"{_BRAND} account, you can safely ignore this email.\n\n"
        f"{_SIGNOFF}"
    )
    return subject, body


def password_reset_email(name: str | None, reset_url: str) -> tuple[str, str]:
    """Email containing a one-time link to choose a new password."""
    subject = f"Reset your {_BRAND} password"
    body = (
        f"{_greeting(name)}\n\n"
        f"We received a request to reset the password for your {_BRAND} account.\n\n"
        "Choose a new password using the link below:\n\n"
        f"{reset_url}\n\n"
        "If the link does not open, copy and paste the full address into your "
        "browser.\n\n"
        "This link will expire shortly for your security. If you did not request "
        "a password reset, you can safely ignore this email -- your current "
        "password will remain unchanged.\n\n"
        f"{_SIGNOFF}"
    )
    return subject, body
