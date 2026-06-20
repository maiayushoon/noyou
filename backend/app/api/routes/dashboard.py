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
from ...schemas.dashboard import DashboardSummary
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

    last_scan = db.scalar(
        select(Scan)
        .where(Scan.user_id == uid, Scan.status == "completed")
        .order_by(Scan.finished_at.desc())
        .limit(1)
    )

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
        top_alerts=top_alerts,
        recent_high_risk=recent_high_risk,
    )
