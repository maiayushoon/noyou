from datetime import datetime, timezone

from app.services.scoring import (
    ScoredMention,
    compute_score,
    reputation_band,
    risk_band,
)

NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def sm(sentiment, risk=0, conf=1.0, published=None, status="active"):
    return ScoredMention(sentiment=sentiment, risk_level=risk, confidence=conf,
                         published_at=published or NOW, status=status)


def test_clean_profile_is_100():
    assert compute_score([sm("positive"), sm("neutral")], NOW) >= 99


def test_negative_high_risk_drops_score():
    score = compute_score([sm("negative", risk=5)], NOW)
    assert score < 100


def test_critical_band():
    mentions = [sm("negative", risk=5) for _ in range(5)]
    score = compute_score(mentions, NOW)
    assert risk_band(score) in ("high", "critical")


def test_removed_mentions_ignored():
    active = compute_score([sm("negative", risk=5)], NOW)
    removed = compute_score([sm("negative", risk=5, status="removed")], NOW)
    assert removed > active
    assert removed == 100.0


def test_score_clamped_to_zero():
    mentions = [sm("negative", risk=5) for _ in range(50)]
    assert compute_score(mentions, NOW) >= 0.0


def test_recency_softens_old_damage():
    old = sm("negative", risk=5, published=datetime(2023, 1, 1, tzinfo=timezone.utc))
    new = sm("negative", risk=5, published=NOW)
    assert compute_score([old], NOW) > compute_score([new], NOW)


def test_bands():
    assert risk_band(90) == "low"
    assert risk_band(70) == "medium"
    assert risk_band(50) == "high"
    assert risk_band(20) == "critical"


def test_reputation_band_is_quality_oriented():
    # Higher score = better band. A perfect score must read as excellent, never "at risk".
    assert reputation_band(100) == "excellent"
    assert reputation_band(85) == "excellent"
    assert reputation_band(75) == "high"
    assert reputation_band(60) == "medium"
    assert reputation_band(40) == "low"
    assert reputation_band(10) == "critical"


def test_reputation_band_is_monotonic():
    order = ["critical", "low", "medium", "high", "excellent"]
    seen = [reputation_band(s) for s in range(0, 101, 5)]
    indices = [order.index(b) for b in seen]
    assert indices == sorted(indices)  # never gets worse as score rises
