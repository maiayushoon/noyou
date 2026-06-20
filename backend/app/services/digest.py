"""Weekly digest — a small, non-sensitive reputation summary emailed to each user.

This is a retention/engagement feature: a once-a-week nudge that pulls the user
back to their dashboard with the few numbers that actually matter (score and its
weekly change, new high-risk mentions, the single most important issue, and how
active their connected accounts were).

Two entry points:

* :func:`build_user_digest` -- pure read: assemble the summary dict for one user.
  Carries ONLY aggregate figures (score, deltas, counts, one issue title). It
  never includes tokens, secrets, raw content, or private links.
* :func:`send_weekly_digests` -- iterate active users and dispatch one digest email
  each via the existing notifications dispatcher. A failure for one user is logged
  and swallowed so the rest still receive theirs. Respects ``settings.digest_enabled``.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.analysis import Analysis
from ..models.linked_account import LinkedAccount
from ..models.mention import Mention
from ..models.scan import Scan
from ..models.user import User
from ..notifications.dispatcher import dispatch_alert
from .email_templates import weekly_digest_email
from .scoring import reputation_band

logger = logging.getLogger("noyou.digest")

DIGEST_WINDOW_DAYS = 7
HIGH_RISK_THRESHOLD = 4  # risk_level >= this is "high-risk" (matches the dashboard)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    """Normalize a possibly-naive DB datetime to UTC-aware for safe comparison."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def build_user_digest(db: Session, user: User) -> dict:
    """Assemble the weekly digest summary for ``user``.

    Returns a small dict of aggregate, non-sensitive figures:

    * ``current_score`` / ``band`` -- the user's latest reputation score and label.
    * ``score_delta``              -- change vs. the score ~a week ago (0.0 if no
                                      earlier baseline exists).
    * ``new_high_risk_mentions``   -- count of high-risk mentions discovered in the
                                      last 7 days.
    * ``top_issue``                -- title of the single most important open issue
                                      (highest-risk recent mention), or ``None``.
    * ``connected_account_activity`` -- count of owned-content mentions discovered
                                      from the user's connected accounts this week.
    """
    now = _utcnow()
    cutoff = now - timedelta(days=DIGEST_WINDOW_DAYS)
    uid = user.id

    current_score = user.reputation_score

    # Weekly delta: current score minus the score as of ~a week ago. We take the
    # score_after of the most recent completed scan at or before the cutoff; if the
    # user has no scan that old, there is no baseline and the delta is 0.0.
    baseline_score = db.scalar(
        select(Scan.score_after)
        .where(
            Scan.user_id == uid,
            Scan.status == "completed",
            Scan.score_after.is_not(None),
            Scan.finished_at <= cutoff,
        )
        .order_by(Scan.finished_at.desc())
        .limit(1)
    )
    score_delta = round(current_score - baseline_score, 1) if baseline_score is not None else 0.0

    # New high-risk mentions discovered in the window.
    new_high_risk = db.scalar(
        select(func.count())
        .select_from(Mention)
        .join(Analysis, Analysis.mention_id == Mention.id)
        .where(
            Mention.user_id == uid,
            Mention.discovered_at >= cutoff,
            Analysis.risk_level >= HIGH_RISK_THRESHOLD,
        )
    ) or 0

    # Single most important issue: highest-risk recent mention still active.
    top_row = db.execute(
        select(Mention.title, Mention.source, Analysis.risk_category, Analysis.risk_level)
        .join(Analysis, Analysis.mention_id == Mention.id)
        .where(
            Mention.user_id == uid,
            Mention.status == "active",
            Analysis.risk_level >= 3,
        )
        .order_by(Analysis.risk_level.desc(), Mention.discovered_at.desc())
        .limit(1)
    ).first()
    top_issue: str | None = None
    if top_row is not None:
        title, src, category, _level = top_row
        top_issue = (title or "").strip() or f"{category} risk on {src}"

    # Connected-account activity: owned-content mentions found this week.
    connected_activity = db.scalar(
        select(func.count())
        .select_from(Mention)
        .where(
            Mention.user_id == uid,
            Mention.discovered_at >= cutoff,
            Mention.source.like("%\\_owned", escape="\\"),
        )
    ) or 0

    return {
        "current_score": current_score,
        "band": reputation_band(current_score),
        "score_delta": score_delta,
        "new_high_risk_mentions": int(new_high_risk),
        "top_issue": top_issue,
        "connected_account_activity": int(connected_activity),
    }


def send_user_digest(db: Session, user: User) -> bool:
    """Build and dispatch one user's digest. Returns True if the email was sent."""
    digest = build_user_digest(db, user)
    subject, body = weekly_digest_email(user.full_name, digest)
    return dispatch_alert(user.email, subject, body)


def send_weekly_digests(db: Session) -> int:
    """Send the weekly digest to every active user. Returns the number sent.

    Idempotent and defensive: respects ``settings.digest_enabled`` and isolates
    each user so one failure never stops the rest. Never raises.
    """
    if not settings.digest_enabled:
        logger.info("Weekly digest skipped: digest_enabled is False")
        return 0

    users = db.scalars(select(User).where(User.is_active == True)).all()  # noqa: E712
    sent = 0
    for user in users:
        try:
            if send_user_digest(db, user):
                sent += 1
        except Exception:
            # One user's failure must not stop the rest.
            logger.exception("weekly digest failed for user %s", user.id)
    logger.info("Weekly digest dispatched to %d/%d active user(s)", sent, len(users))
    return sent
