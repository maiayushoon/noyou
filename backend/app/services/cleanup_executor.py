"""Automated cleanup execution (Pro+ feature).

Real platform deletion would require OAuth *write* scopes we don't hold, so
"automated" here means: auto-**apply** the actions that are safe and fully
self-serviceable (they only mutate the user's own dashboard state), and
**draft** the rest (a templated removal-request message the user can send).

Lifecycle over the user's :class:`CleanupAction` rows whose ``status`` is in
``("suggested", "in_progress")``:

* ``archive`` — fully automatable: it's the user's own dashboard state. Sets the
  linked :class:`Mention` to ``archived`` and the action to ``completed``
  (``outcome="executed"``).
* ``monitor`` — mark the action ``in_progress`` so it's actively tracked
  (``outcome="executed"``).
* ``request_removal`` / ``dispute`` / ``delete_post`` — we cannot submit to third
  parties, so we generate a ``DRAFT:`` removal-request message (from the mention's
  source/url) onto ``action.instructions`` and set the action ``in_progress``
  (``outcome="drafted"``).

Anything else is skipped (``outcome="skipped"``). After mutating state the user's
reputation score is recomputed. With ``dry_run=True`` the outcomes are computed but
nothing is persisted.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.cleanup import CleanupAction
from ..models.mention import Mention
from ..models.user import User

# Actions we can fully apply on the user's behalf (only touch their own state).
_AUTO_APPLY = {"archive", "monitor"}
# Actions that require a third party — we can only prepare a draft.
_DRAFT_ONLY = {"request_removal", "dispute", "delete_post"}

# CleanupAction statuses eligible for execution.
_PENDING_STATUSES = ("suggested", "in_progress")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _draft_message(mention: Mention | None, action_type: str) -> str:
    """Build a short, templated removal-request draft for a mention.

    Returns a single string prefixed with ``DRAFT:`` so the UI can render it as a
    ready-to-send message rather than generic instructions.
    """
    source = (mention.source if mention else None) or "the platform"
    url = (mention.url if mention else None) or "(URL unavailable)"
    title = (mention.title if mention else None) or "the content in question"

    verb = {
        "request_removal": "request the removal of",
        "delete_post": "request the deletion of",
        "dispute": "dispute and request the correction or removal of",
    }.get(action_type, "request the removal of")

    return (
        f"DRAFT: Hello, I am writing to {verb} content about me hosted on {source}. "
        f"Reference: {title} ({url}). This content is inaccurate, outdated, or harmful "
        "to my reputation, and I am requesting that it be removed or corrected under your "
        "content and privacy policies. Please confirm receipt and the steps required. "
        "Thank you."
    )


def execute_pending(db: Session, user: User, dry_run: bool = False) -> dict:
    """Apply/draft the user's pending cleanup actions.

    Returns a summary dict::

        {
          "executed": int,   # archive/monitor actions applied
          "drafted": int,    # removal/dispute/delete drafts prepared
          "skipped": int,    # actions we didn't act on
          "dry_run": bool,
          "details": [{"action_id", "action_type", "outcome", "note"}, ...],
        }

    When ``dry_run`` is true the outcomes are computed exactly as they would be,
    but no rows are mutated and the score is not recomputed.
    """
    executed = 0
    drafted = 0
    skipped = 0
    details: list[dict] = []
    mutated = False

    actions = db.scalars(
        select(CleanupAction)
        .where(
            CleanupAction.user_id == user.id,
            CleanupAction.status.in_(_PENDING_STATUSES),
        )
        .order_by(CleanupAction.created_at.asc())
    ).all()

    for action in actions:
        action_type = (action.action_type or "").strip().lower()
        # Be defensive: the linked mention may have been deleted out from under us.
        mention = db.get(Mention, action.mention_id) if action.mention_id else None

        if action_type == "archive":
            note = "Mention archived and action completed."
            if not dry_run:
                if mention is not None and mention.user_id == user.id:
                    mention.status = "archived"
                    db.add(mention)
                action.status = "completed"
                action.completed_at = _utcnow()
                action.automated = True
                db.add(action)
                mutated = True
            executed += 1
            details.append(
                {
                    "action_id": action.id,
                    "action_type": action_type,
                    "outcome": "executed",
                    "note": note,
                }
            )

        elif action_type == "monitor":
            note = "Mention is now actively tracked."
            if not dry_run:
                action.status = "in_progress"
                action.automated = True
                db.add(action)
                mutated = True
            executed += 1
            details.append(
                {
                    "action_id": action.id,
                    "action_type": action_type,
                    "outcome": "executed",
                    "note": note,
                }
            )

        elif action_type in _DRAFT_ONLY:
            draft = _draft_message(mention, action_type)
            note = "Removal-request draft prepared; submit it to the platform."
            if not dry_run:
                action.instructions = draft
                action.status = "in_progress"
                action.automated = True
                db.add(action)
                mutated = True
            drafted += 1
            details.append(
                {
                    "action_id": action.id,
                    "action_type": action_type,
                    "outcome": "drafted",
                    "note": note,
                }
            )

        else:
            skipped += 1
            details.append(
                {
                    "action_id": action.id,
                    "action_type": action_type,
                    "outcome": "skipped",
                    "note": "No automated handler for this action type.",
                }
            )

    if not dry_run and mutated:
        db.commit()
        # Archived mentions no longer drag the score — recompute from the corpus.
        # Imported lazily to avoid a circular import (scanning imports services).
        from .scanning import recompute_user_score

        recompute_user_score(db, user)

    return {
        "executed": executed,
        "drafted": drafted,
        "skipped": skipped,
        "dry_run": dry_run,
        "details": details,
    }
