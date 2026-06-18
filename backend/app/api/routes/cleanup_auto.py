"""Automated cleanup execution endpoint (Pro+).

Shares the ``/cleanup`` prefix with :mod:`app.api.routes.cleanup`; this router must
be included *after* ``cleanup.router`` (the same pattern as ``auth_extra`` vs
``auth``). Gated to paying tiers via :func:`require_plan`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.plans import require_plan
from ...models.user import User
from ...services.cleanup_executor import execute_pending
from ..deps import get_current_user  # noqa: F401  (auth enforced via require_plan)

router = APIRouter(prefix="/cleanup", tags=["cleanup"])


@router.post("/auto-execute")
def auto_execute(
    dry_run: bool = Query(default=False, description="Compute outcomes without persisting."),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_plan("pro", "premium", "enterprise")),
) -> dict:
    """Auto-apply safe cleanup actions and draft the rest for the current user.

    Returns a summary ``{executed, drafted, skipped, dry_run, details}``. Requires a
    Pro, Premium, or Enterprise plan (402 otherwise).
    """
    return execute_pending(db, current_user, dry_run=dry_run)
