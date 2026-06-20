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


def _format_delta(delta: float) -> str:
    """Human-readable signed score change, e.g. '+3.4', '-2.0', 'no change'."""
    if delta > 0:
        return f"up {delta:+.1f} points"
    if delta < 0:
        return f"down {delta:+.1f} points"
    return "unchanged"


def weekly_digest_email(name: str | None, digest: dict) -> tuple[str, str]:
    """Weekly reputation summary email built from a ``build_user_digest`` dict.

    The ``digest`` carries only aggregate, non-sensitive figures (score, deltas,
    counts, one issue title) -- never tokens, links to private content, or secrets.
    """
    score = digest.get("current_score", 0.0)
    band = (digest.get("band") or "").replace("_", " ").title()
    delta = float(digest.get("score_delta", 0.0) or 0.0)
    new_high_risk = int(digest.get("new_high_risk_mentions", 0) or 0)
    top_issue = (digest.get("top_issue") or "").strip()
    owned_activity = int(digest.get("connected_account_activity", 0) or 0)

    subject = f"Your weekly {_BRAND} reputation digest"

    band_part = f" ({band})" if band else ""
    lines = [
        _greeting(name),
        "",
        f"Here is your {_BRAND} reputation summary for the past week.",
        "",
        f"Reputation score: {score:.0f}/100{band_part} -- {_format_delta(delta)} since last week.",
        f"New high-risk mentions (last 7 days): {new_high_risk}",
        f"Activity on your connected accounts: {owned_activity}",
    ]
    if top_issue:
        lines += ["", f"Most important issue to review: {top_issue}"]
    lines += [
        "",
        "Open your dashboard to review the details and recommended actions.",
        "",
        _SIGNOFF,
    ]
    return subject, "\n".join(lines)


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
