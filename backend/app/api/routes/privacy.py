"""Privacy & compliance endpoints — GDPR / CCPA data rights.

Exposes the two user-facing data-protection rights that a digital-reputation
product is legally obliged to honour:

* ``GET  /privacy/export``   — *right to data portability* (GDPR Art. 20,
  CCPA "right to know"). Returns the authenticated user's full record as a
  single JSON object so they can download and keep a copy of everything we
  hold about them.
* ``DELETE /privacy/account`` — *right to erasure / "right to be forgotten"*
  (GDPR Art. 17, CCPA "right to delete"). Permanently removes the user and
  every row that hangs off them.

Both endpoints require a valid JWT and operate strictly on
``current_user.id`` — a user can only ever export or delete their own data.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.account import Account
from ...models.alert import Alert
from ...models.analysis import Analysis
from ...models.cleanup import CleanupAction
from ...models.mention import Mention
from ...models.scan import Scan
from ...models.user import User
from ..deps import get_current_user

router = APIRouter(prefix="/privacy", tags=["privacy"])


def _iso(value: datetime | None) -> str | None:
    """Serialize a datetime to an ISO-8601 string (or ``None``)."""
    return value.isoformat() if value is not None else None


def _serialize_user(user: User) -> dict:
    """The user's own profile record (credentials are never exported)."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": getattr(user, "is_verified", None),
        "plan": user.plan,
        "reputation_score": user.reputation_score,
        "created_at": _iso(user.created_at),
        "updated_at": _iso(user.updated_at),
    }


def _serialize_account(account: Account) -> dict:
    """A linked/monitored identity. OAuth tokens are deliberately omitted."""
    return {
        "id": account.id,
        "platform": account.platform,
        "handle": account.handle,
        "display_name": account.display_name,
        "profile_url": account.profile_url,
        "is_active": account.is_active,
        "created_at": _iso(account.created_at),
    }


def _serialize_analysis(analysis: Analysis | None) -> dict | None:
    """The AI analysis attached to a mention, if one exists."""
    if analysis is None:
        return None
    return {
        "id": analysis.id,
        "sentiment": analysis.sentiment,
        "sentiment_score": analysis.sentiment_score,
        "risk_level": analysis.risk_level,
        "risk_category": analysis.risk_category,
        "context": analysis.context,
        "summary": analysis.summary,
        "recommendation": analysis.recommendation,
        "analyzer": analysis.analyzer,
        "confidence": analysis.confidence,
        "created_at": _iso(analysis.created_at),
    }


def _serialize_mention(mention: Mention) -> dict:
    """A discovered piece of content, with its analysis inlined."""
    return {
        "id": mention.id,
        "scan_id": mention.scan_id,
        "source": mention.source,
        "external_id": mention.external_id,
        "url": mention.url,
        "author": mention.author,
        "title": mention.title,
        "content": mention.content,
        "status": mention.status,
        "published_at": _iso(mention.published_at),
        "discovered_at": _iso(mention.discovered_at),
        "analysis": _serialize_analysis(mention.analysis),
    }


def _serialize_alert(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "mention_id": alert.mention_id,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "is_read": alert.is_read,
        "notified": alert.notified,
        "created_at": _iso(alert.created_at),
    }


def _serialize_cleanup(action: CleanupAction) -> dict:
    return {
        "id": action.id,
        "mention_id": action.mention_id,
        "action_type": action.action_type,
        "title": action.title,
        "instructions": action.instructions,
        "status": action.status,
        "automated": action.automated,
        "created_at": _iso(action.created_at),
        "completed_at": _iso(action.completed_at),
    }


def _serialize_scan(scan: Scan) -> dict:
    return {
        "id": scan.id,
        "status": scan.status,
        "trigger": scan.trigger,
        "connectors_used": scan.connectors_used,
        "mentions_found": scan.mentions_found,
        "new_mentions": scan.new_mentions,
        "score_before": scan.score_before,
        "score_after": scan.score_after,
        "error": scan.error,
        "started_at": _iso(scan.started_at),
        "finished_at": _iso(scan.finished_at),
    }


@router.get("/export")
def export_my_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Export every record we hold for the current user as one JSON object.

    Implements the GDPR *right to data portability* (Art. 20) and the CCPA
    *right to know*. Every collection is queried by ``user_id`` so the export
    is scoped exclusively to the requesting user, and timestamps are returned
    as ISO-8601 strings for a portable, machine-readable archive.
    """
    # Mentions carry their analysis; eager-loading is unnecessary here because
    # the relationship is resolved per-row during serialization.
    mentions = db.scalars(
        select(Mention)
        .where(Mention.user_id == current_user.id)
        .order_by(Mention.discovered_at.desc())
    ).all()

    accounts = db.scalars(
        select(Account)
        .where(Account.user_id == current_user.id)
        .order_by(Account.created_at.desc())
    ).all()

    alerts = db.scalars(
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
    ).all()

    cleanup_actions = db.scalars(
        select(CleanupAction)
        .where(CleanupAction.user_id == current_user.id)
        .order_by(CleanupAction.created_at.desc())
    ).all()

    scans = db.scalars(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.started_at.desc())
    ).all()

    return {
        "export_format": "noyou.data-export.v1",
        "generated_at": _iso(datetime.now().astimezone()),
        "profile": _serialize_user(current_user),
        "accounts": [_serialize_account(a) for a in accounts],
        "mentions": [_serialize_mention(m) for m in mentions],
        "alerts": [_serialize_alert(a) for a in alerts],
        "cleanup_actions": [_serialize_cleanup(c) for c in cleanup_actions],
        "scans": [_serialize_scan(s) for s in scans],
        "counts": {
            "accounts": len(accounts),
            "mentions": len(mentions),
            "alerts": len(alerts),
            "cleanup_actions": len(cleanup_actions),
            "scans": len(scans),
        },
    }


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Permanently delete the current user and all associated data.

    Implements the GDPR *right to erasure* (Art. 17) and the CCPA *right to
    delete*. The ``User`` relationships are declared with
    ``cascade="all, delete-orphan"``, so deleting the user cascades to their
    accounts, mentions (and each mention's analysis, alerts and cleanup
    actions), top-level alerts and scans in a single transaction.

    This action is irreversible — there is no soft-delete. Returns
    ``204 No Content``.
    """
    db.delete(current_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
