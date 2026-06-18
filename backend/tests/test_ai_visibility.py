"""Tests for the AI Visibility (GEO/AEO) feature.

Follows the patterns in test_prod_features.py: SessionLocal + a _set_plan helper to
promote a user's plan, and the shared auth_client/client fixtures from conftest.
"""
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.analysis import Analysis
from app.models.mention import Mention
from app.models.user import User


def _set_plan(email: str, plan: str) -> None:
    """Promote a user's plan directly in the DB (no billing in the test path)."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.plan = plan
        db.add(user)
        db.commit()
    finally:
        db.close()


def _seed_mentions(email: str) -> None:
    """Give the user a handful of mentions across sources, with analysis attached."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        seeds = [
            ("web", "https://testuser.com/about", "positive", 0),
            ("linkedin", "https://linkedin.com/in/testuser", "positive", 0),
            ("hackernews", "https://news.ycombinator.com/item?id=1", "neutral", 1),
            ("reddit_public", "https://reddit.com/r/x/comments/1", "positive", 1),
            ("youtube", "https://youtube.com/watch?v=abc", "neutral", 0),
        ]
        for source, url, sentiment, risk in seeds:
            mention = Mention(
                user_id=user.id,
                source=source,
                external_id=url,
                url=url,
                title="About Test User",
                content="Test User is a founder building things.",
                discovered_at=datetime.now(timezone.utc),
            )
            db.add(mention)
            db.flush()
            db.add(
                Analysis(
                    mention_id=mention.id,
                    sentiment=sentiment,
                    sentiment_score=0.5 if sentiment == "positive" else 0.0,
                    risk_level=risk,
                    risk_category="none",
                    analyzer="rule_based",
                    confidence=0.7,
                )
            )
        db.commit()
    finally:
        db.close()


def test_ai_visibility_gated_for_free(auth_client):
    # AI Visibility is a Pro+ feature; a free user gets a 402 upgrade-required.
    r = auth_client.get("/api/v1/ai-visibility")
    assert r.status_code == 402


def test_ai_visibility_works_for_pro(auth_client):
    _set_plan("t@test.com", "pro")
    _seed_mentions("t@test.com")

    r = auth_client.get("/api/v1/ai-visibility")
    assert r.status_code == 200
    body = r.json()

    # Brand resolves to the user's full name from the auth_client fixture.
    assert body["brand"] == "Test User"
    # Score is a real 0-100 number.
    assert 0.0 <= body["ai_visibility_score"] <= 100.0
    assert body["band"] in ("low", "medium", "high", "excellent")
    # Heuristic-only path (no LLM key configured in tests).
    assert body["llm_used"] is False
    # Signals and tailored recommendations are returned.
    assert len(body["signals"]) >= 5
    assert all({"name", "present", "weight", "detail"} <= set(s) for s in body["signals"])
    assert len(body["recommendations"]) >= 1
    assert isinstance(body["summary"], str) and body["summary"]


def test_ai_visibility_pro_with_no_mentions_still_ok(auth_client):
    # Even with no mentions, a Pro user gets a valid low-visibility assessment (never raises).
    _set_plan("t@test.com", "pro")
    r = auth_client.get("/api/v1/ai-visibility")
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["ai_visibility_score"] <= 100.0
    assert len(body["recommendations"]) >= 1
