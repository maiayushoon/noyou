"""Competitor benchmarking — compare a user's reputation against rivals.

Premium feature. For the requesting user we reuse their CURRENT stored mentions +
analyses (no fresh scan) to compute their score; for each tracked competitor we run
a small LIVE scan across the active connectors, analyze each result IN MEMORY, and
compute a score + sentiment breakdown without ever persisting competitor mentions.

The pipeline mirrors ``services.scanning`` (relevance gate, analyzer, ``ScoredMention``
+ ``compute_score``) but keeps everything ephemeral, and is resilient — a connector
that raises is skipped so one bad source never sinks the whole report.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..analysis import get_analyzer
from ..analysis.base import AnalysisInput
from ..connectors import get_active_connectors
from ..core.config import settings
from ..models.analysis import Analysis
from ..models.competitor import Competitor
from ..models.mention import Mention
from ..models.user import User
from .relevance import is_relevant
from .scoring import ScoredMention, compute_score, reputation_band

logger = logging.getLogger("noyou.benchmark")

# Keep competitor live-scans light: a few results per connector is plenty for a
# representative score without hammering external sources.
COMPETITOR_QUERY_LIMIT = 10


def _empty_sentiment() -> dict[str, int]:
    return {"positive": 0, "neutral": 0, "negative": 0}


def _user_entry(db: Session, user: User) -> dict:
    """Build the ``is_you`` entry from the user's already-stored mentions + analyses."""
    rows = db.execute(
        select(
            Analysis.sentiment,
            Analysis.risk_level,
            Analysis.confidence,
            Mention.published_at,
            Mention.status,
        )
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == user.id)
    ).all()

    scored = [
        ScoredMention(
            sentiment=r.sentiment,
            risk_level=r.risk_level,
            confidence=r.confidence,
            published_at=r.published_at,
            status=r.status,
        )
        for r in rows
    ]
    sentiment = _empty_sentiment()
    for r in rows:
        if r.status in {"removed", "archived"}:
            continue
        if r.sentiment in sentiment:
            sentiment[r.sentiment] += 1

    score = compute_score(scored)
    return {
        "name": user.full_name or user.email.split("@")[0],
        "is_you": True,
        "reputation_score": score,
        "band": reputation_band(score),
        "total_mentions": sum(sentiment.values()),
        "sentiment": sentiment,
    }


def _competitor_entry(name: str) -> dict:
    """Live-scan a competitor name in memory and compute its score + sentiment."""
    analyzer = get_analyzer()
    scored: list[ScoredMention] = []
    sentiment = _empty_sentiment()

    for connector in get_active_connectors():
        try:
            raw_mentions = connector.search(name, limit=COMPETITOR_QUERY_LIMIT)
        except Exception as exc:
            logger.warning("benchmark connector %s failed for %r: %s", connector.name, name, exc)
            continue

        for raw in raw_mentions:
            # Same relevance gate scanning uses; the synthetic demo connector
            # bypasses it so the offline path still yields a benchmark.
            if (
                settings.relevance_filter
                and connector.name != "demo"
                and not is_relevant(name, f"{raw.title or ''} {raw.content or ''}")
            ):
                continue

            try:
                result = analyzer.analyze(
                    AnalysisInput(
                        content=raw.content,
                        title=raw.title,
                        source=raw.source,
                        author=raw.author,
                        subject_name=name,
                    )
                )
            except Exception as exc:
                logger.warning("benchmark analyze failed for %r: %s", name, exc)
                continue

            scored.append(
                ScoredMention(
                    sentiment=result.sentiment,
                    risk_level=result.risk_level,
                    confidence=result.confidence,
                    published_at=raw.published_at,
                )
            )
            if result.sentiment in sentiment:
                sentiment[result.sentiment] += 1

    score = compute_score(scored)
    return {
        "name": name,
        "is_you": False,
        "reputation_score": score,
        "band": reputation_band(score),
        "total_mentions": sum(sentiment.values()),
        "sentiment": sentiment,
    }


def run_benchmark(db: Session, user: User) -> dict:
    """Build a benchmark report: the user first, then competitors sorted by score desc."""
    entries = [_user_entry(db, user)]

    competitors = db.scalars(
        select(Competitor).where(Competitor.user_id == user.id).order_by(Competitor.created_at)
    ).all()

    competitor_entries = [_competitor_entry(c.name) for c in competitors]
    competitor_entries.sort(key=lambda e: e["reputation_score"], reverse=True)
    entries.extend(competitor_entries)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
