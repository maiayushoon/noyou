from datetime import datetime, timezone

from app.services.scoring import ScoredMention, compute_score, risk_band

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
