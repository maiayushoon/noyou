"""Reputation scoring engine.

Generalises the blueprint's algorithm::

    score = 100
    for m in mentions:
        if m.sentiment == "negative": score -= 10 * m.risk_level
        elif m.sentiment == "neutral": score -= 3 * m.risk_level

The naive version is unbounded and over-punishes: a handful of severe mentions drives
the score straight to 0, which isn't how reputation works (you don't have *zero*
reputation because of five bad posts). We keep the spirit — negatives and risk hurt,
positives help — but make the number trustworthy with four improvements:

1. **Saturating penalty** — damage accumulates with diminishing returns and maps
   through ``100 * damage / (damage + K)`` so the score degrades smoothly and never
   slams to 0 from a few items.
2. **Recency weighting** — a damaging post from 2 years ago hurts less than one today
   (≈120-day half-life).
3. **Positive lift** — genuinely positive coverage repairs the score (capped).
4. **Confidence weighting** — low-confidence AI calls move the score less.

The result is clamped to 0-100 and bucketed into a risk band for the UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

BASE_SCORE = 100.0
NEGATIVE_WEIGHT = 1.0             # risk-points of damage per negative mention
NEUTRAL_WEIGHT = 0.25            # neutral-but-risky content nicks the score
POSITIVE_LIFT = 1.2              # repair per positive mention (pre-cap)
POSITIVE_LIFT_CAP = 10.0        # positives can only recover so much
SATURATION = 18.0               # K in the saturating curve — lower = more sensitive
RECENCY_HALF_LIFE_DAYS = 120.0  # impact halves every ~4 months


@dataclass
class ScoredMention:
    sentiment: str
    risk_level: int
    confidence: float = 0.6
    published_at: datetime | None = None
    status: str = "active"


def _recency_weight(published_at: datetime | None, now: datetime) -> float:
    if published_at is None:
        return 0.7  # unknown date → moderate weight
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (now - published_at).total_seconds() / 86400.0)
    return 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)


def risk_band(score: float) -> str:
    """RISK band — *low* risk is good. Used internally where risk semantics are wanted.

    Note: this is the inverse of how a user reads a reputation score, so it must NOT
    be sent to the UI as a quality label. Use :func:`reputation_band` for anything the
    dashboard renders.
    """
    if score >= 80:
        return "low"
    if score >= 60:
        return "medium"
    if score >= 40:
        return "high"
    return "critical"


def reputation_band(score: float) -> str:
    """QUALITY band for a 0-100 reputation score — *higher is better*.

    This is what the UI shows. The keys line up with the dashboard's color/label map:
    ``excellent``/``high`` are green (strong), ``medium`` amber (fair), ``low`` orange
    (at risk), ``critical`` red. A score of 100 reads as "Excellent", not "At risk".
    """
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "low"
    return "critical"


def compute_score(mentions: list[ScoredMention], now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    damage = 0.0
    positive_accum = 0.0

    for m in mentions:
        # Mentions the user has already cleaned up no longer drag the score.
        if m.status in {"removed", "archived"}:
            continue

        recency = _recency_weight(m.published_at, now)
        conf = max(0.2, min(1.0, m.confidence))
        weight = recency * conf

        if m.sentiment == "negative":
            damage += NEGATIVE_WEIGHT * max(1, m.risk_level) * weight
        elif m.sentiment == "neutral":
            damage += NEUTRAL_WEIGHT * max(0, m.risk_level) * weight
        elif m.sentiment == "positive":
            positive_accum += POSITIVE_LIFT * weight

    # Saturating penalty: smooth, bounded, never zeroes out from a few items.
    penalty = 100.0 * damage / (damage + SATURATION) if damage > 0 else 0.0
    score = BASE_SCORE - penalty + min(POSITIVE_LIFT_CAP, positive_accum)
    return round(max(0.0, min(100.0, score)), 1)


def score_breakdown(mentions: list[ScoredMention], now: datetime | None = None) -> dict:
    """Per-category contribution, useful for the dashboard explainer."""
    now = now or datetime.now(timezone.utc)
    total = len(mentions)
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    high_risk = 0
    for m in mentions:
        counts[m.sentiment] = counts.get(m.sentiment, 0) + 1
        if m.risk_level >= 4:
            high_risk += 1
    score = compute_score(mentions, now)
    return {
        "score": score,
        "band": reputation_band(score),
        "total_mentions": total,
        "sentiment_counts": counts,
        "high_risk_count": high_risk,
        "positive_ratio": round(counts["positive"] / total, 2) if total else 0.0,
    }
