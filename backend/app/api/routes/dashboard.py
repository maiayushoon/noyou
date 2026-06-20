from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ...core.database import get_db
from ...models.alert import Alert
from ...models.analysis import Analysis
from ...models.cleanup import CleanupAction
from ...models.mention import Mention
from ...models.scan import Scan
from ...models.user import User
from ...schemas.dashboard import DashboardSummary, ScoreTrendPoint
from ...services.scoring import reputation_band
from ..deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary)
def get_dashboard(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    uid = current_user.id

    total_mentions = db.scalar(
        select(func.count()).select_from(Mention).where(Mention.user_id == uid)
    ) or 0

    sentiment_rows = db.execute(
        select(Analysis.sentiment, func.count())
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == uid)
        .group_by(Analysis.sentiment)
    ).all()
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for sentiment, count in sentiment_rows:
        sentiment_counts[sentiment] = count

    high_risk_count = db.scalar(
        select(func.count())
        .select_from(Analysis)
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == uid, Analysis.risk_level >= 4)
    ) or 0

    unread_alerts = db.scalar(
        select(func.count())
        .select_from(Alert)
        .where(Alert.user_id == uid, Alert.is_read == False)  # noqa: E712
    ) or 0

    active_cleanup = db.scalar(
        select(func.count())
        .select_from(CleanupAction)
        .where(CleanupAction.user_id == uid, CleanupAction.status.in_(("suggested", "in_progress")))
    ) or 0

    # Recent completed scans (newest -> oldest), one query, drives the hero
    # sparkline AND the score delta. We take up to 8 so the trend has history;
    # the first row is the most recent scan used for delta/previous_score.
    recent_scans = db.scalars(
        select(Scan)
        .where(
            Scan.user_id == uid,
            Scan.status == "completed",
            Scan.score_after.is_not(None),
        )
        .order_by(Scan.finished_at.desc())
        .limit(8)
    ).all()

    last_scan = recent_scans[0] if recent_scans else None

    # Delta + previous score come from the most recent completed scan.
    score_delta = 0.0
    previous_score: float | None = None
    if last_scan is not None and last_scan.score_after is not None:
        if last_scan.score_before is not None:
            previous_score = last_scan.score_before
            score_delta = round(last_scan.score_after - last_scan.score_before, 1)

    # Trend: oldest -> newest for left-to-right rendering.
    score_trend = [
        ScoreTrendPoint(
            date=(s.finished_at or s.started_at).isoformat(),
            score=s.score_after,
        )
        for s in reversed(recent_scans)
    ]

    top_alerts = db.scalars(
        select(Alert)
        .where(Alert.user_id == uid)
        .order_by(Alert.is_read.asc(), Alert.created_at.desc())
        .limit(5)
    ).all()

    recent_high_risk = db.scalars(
        select(Mention)
        .options(selectinload(Mention.analysis))
        .join(Analysis, Analysis.mention_id == Mention.id)
        .where(Mention.user_id == uid, Analysis.risk_level >= 3)
        .order_by(Analysis.risk_level.desc(), Mention.discovered_at.desc())
        .limit(5)
    ).all()

    return DashboardSummary(
        reputation_score=current_user.reputation_score,
        band=reputation_band(current_user.reputation_score),
        total_mentions=total_mentions,
        sentiment_counts=sentiment_counts,
        high_risk_count=high_risk_count,
        unread_alerts=unread_alerts,
        active_cleanup_actions=active_cleanup,
        last_scan_at=last_scan.finished_at.isoformat() if last_scan and last_scan.finished_at else None,
        score_delta=score_delta,
        previous_score=previous_score,
        score_trend=score_trend,
        top_alerts=top_alerts,
        recent_high_risk=recent_high_risk,
    )
