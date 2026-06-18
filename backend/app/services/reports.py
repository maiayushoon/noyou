"""Reports & trends — aggregates for the dashboard's charts and exportable reports."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.analysis import Analysis
from ..models.mention import Mention
from ..models.scan import Scan
from ..models.user import User
from .scoring import risk_band


def sentiment_distribution(db: Session, user: User) -> dict[str, int]:
    rows = db.execute(
        select(Analysis.sentiment)
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == user.id)
    ).all()
    dist = {"positive": 0, "neutral": 0, "negative": 0}
    for (sentiment,) in rows:
        dist[sentiment] = dist.get(sentiment, 0) + 1
    return dist


def risk_by_category(db: Session, user: User) -> dict[str, int]:
    rows = db.execute(
        select(Analysis.risk_category)
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == user.id, Analysis.risk_level >= 2)
    ).all()
    dist: dict[str, int] = defaultdict(int)
    for (category,) in rows:
        dist[category] += 1
    return dict(dist)


def mentions_by_source(db: Session, user: User) -> dict[str, int]:
    rows = db.execute(select(Mention.source).where(Mention.user_id == user.id)).all()
    dist: dict[str, int] = defaultdict(int)
    for (source,) in rows:
        dist[source] += 1
    return dict(dist)


def score_history(db: Session, user: User, limit: int = 30) -> list[dict]:
    """Score-after over recent completed scans, oldest→newest, for the trend line."""
    scans = db.scalars(
        select(Scan)
        .where(Scan.user_id == user.id, Scan.status == "completed", Scan.score_after.is_not(None))
        .order_by(Scan.started_at.desc())
        .limit(limit)
    ).all()
    scans = list(reversed(scans))
    return [
        {
            "date": s.finished_at.isoformat() if s.finished_at else s.started_at.isoformat(),
            "score": s.score_after,
            "band": risk_band(s.score_after),
        }
        for s in scans
    ]


def mentions_over_time(db: Session, user: User, days: int = 90) -> list[dict]:
    """Daily count of newly discovered mentions, for the volume sparkline."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.scalars(
        select(Mention.discovered_at).where(
            Mention.user_id == user.id, Mention.discovered_at >= cutoff
        )
    ).all()
    buckets: dict[str, int] = defaultdict(int)
    for dt in rows:
        buckets[dt.date().isoformat()] += 1
    return [{"date": d, "count": c} for d, c in sorted(buckets.items())]


def full_report(db: Session, user: User) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reputation_score": user.reputation_score,
        "band": risk_band(user.reputation_score),
        "sentiment_distribution": sentiment_distribution(db, user),
        "risk_by_category": risk_by_category(db, user),
        "mentions_by_source": mentions_by_source(db, user),
        "score_history": score_history(db, user),
        "mentions_over_time": mentions_over_time(db, user),
    }
