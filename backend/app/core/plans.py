"""Subscription plan gating and scan-quota enforcement (monetization tier).

Defines the per-plan feature matrix (``PLAN_LIMITS``) for the four subscription
tiers — ``free | pro | premium | enterprise`` — plus FastAPI dependency factories
that callers attach to routes to gate features by plan, and helpers that enforce a
rolling daily scan quota.

Routes should:
  * ``Depends(require_plan("pro", "premium", "enterprise"))`` to restrict an endpoint
    to paying tiers,
  * ``Depends(require_feature("predictive"))`` to gate a single boolean feature, and
  * call ``enforce_scan_quota(db, current_user)`` at the top of the scan handler.

The numeric value ``-1`` denotes "unlimited" for any count-based limit
(``max_accounts``, ``scans_per_day``); ``"all"`` denotes every connector.
"""
from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Any, Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..api.deps import get_current_user
from ..models.scan import Scan
from ..models.user import User

# Sentinel meaning "no cap" for any count-based limit.
UNLIMITED = -1

# The canonical fallback tier for unknown / unset plans.
DEFAULT_PLAN = "free"


# --- Plan feature matrix --------------------------------------------------
# Each plan maps to the same set of keys so callers can index any feature
# uniformly via ``get_limits(plan)[feature]``.
PLAN_LIMITS: dict[str, dict[str, Any]] = {
    "free": {
        "max_accounts": 1,
        "scans_per_day": 3,
        # Keyless real-data sources are free so the public gets genuine value;
        # keyed/authenticated providers (google, twitter, ...) are paid tiers.
        "connectors": ["demo", "web", "hackernews", "reddit_public"],
        "predictive": False,
        "benchmarking": False,
        "api_access": False,
    },
    "pro": {
        "max_accounts": 5,
        "scans_per_day": 50,
        # "owned" enables the user's own linked-account content (OAuth connections).
        # premium/enterprise get it implicitly via "all".
        "connectors": ["demo", "web", "hackernews", "reddit_public", "google", "twitter", "reddit", "youtube", "owned"],
        "predictive": True,
        # Benchmarking + Teams are surfaced as Pro features in the UI, so Pro unlocks them.
        "benchmarking": True,
        "api_access": False,
    },
    "premium": {
        "max_accounts": 25,
        "scans_per_day": 500,
        "connectors": "all",
        "predictive": True,
        "benchmarking": True,
        "api_access": False,
    },
    "enterprise": {
        "max_accounts": UNLIMITED,
        "scans_per_day": UNLIMITED,
        "connectors": "all",
        "predictive": True,
        "benchmarking": True,
        "api_access": True,
    },
}


def get_limits(plan: str | None) -> dict[str, Any]:
    """Return the limit/feature dict for ``plan``, defaulting to free.

    Unknown, ``None``, or mis-cased plan names fall back to the free tier so a
    bad value can never accidentally unlock paid features.
    """
    if not plan:
        return PLAN_LIMITS[DEFAULT_PLAN]
    return PLAN_LIMITS.get(plan.lower(), PLAN_LIMITS[DEFAULT_PLAN])


def plan_allows_connector(plan: str | None, connector: str) -> bool:
    """Whether ``plan`` may use a given connector by name.

    ``"all"`` grants every connector; otherwise the connector must appear in the
    plan's explicit allow-list (case-insensitive).
    """
    allowed = get_limits(plan)["connectors"]
    if allowed == "all":
        return True
    return connector.strip().lower() in {c.lower() for c in allowed}


# --- Dependency factories -------------------------------------------------
def require_plan(*allowed: str) -> Callable[..., User]:
    """Build a dependency that requires the user's plan to be in ``allowed``.

    Raises ``402 Payment Required`` (the conventional "upgrade required" status)
    when the current user's plan is not whitelisted. Returns the user so the route
    can reuse it without a second ``get_current_user`` dependency.
    """
    allowed_set = {p.lower() for p in allowed}

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if (current_user.plan or DEFAULT_PLAN).lower() not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Upgrade required",
            )
        return current_user

    return _dependency


def require_feature(feature_name: str) -> Callable[..., User]:
    """Build a dependency that requires a boolean/feature flag on the user's plan.

    402s when ``get_limits(user.plan)[feature_name]`` is falsy (missing, ``False``,
    ``0``, empty list, ...). Use for single-feature gates such as
    ``require_feature("predictive")`` or ``require_feature("benchmarking")``.
    """

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if not get_limits(current_user.plan).get(feature_name):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Upgrade required",
            )
        return current_user

    return _dependency


# --- Scan quota -----------------------------------------------------------
def _start_of_utc_day(now: datetime | None = None) -> datetime:
    """Midnight (00:00:00) UTC for the current day, timezone-aware."""
    now = now or datetime.now(timezone.utc)
    return datetime.combine(now.date(), time.min, tzinfo=timezone.utc)


def scans_today(db: Session, user: User) -> int:
    """Count the user's scans started since the start of the current UTC day."""
    day_start = _start_of_utc_day()
    count = db.scalar(
        select(func.count())
        .select_from(Scan)
        .where(Scan.user_id == user.id, Scan.started_at >= day_start)
    )
    return int(count or 0)


def enforce_scan_quota(db: Session, user: User) -> None:
    """Raise 429 when the user has hit their plan's daily scan limit.

    No-ops for unlimited plans (``scans_per_day == UNLIMITED``, e.g. enterprise).
    Call at the very top of the scan-trigger handler, before any work is done.
    """
    limit = get_limits(user.plan)["scans_per_day"]
    if limit == UNLIMITED:
        return
    if scans_today(db, user) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily scan limit reached for your plan",
        )
