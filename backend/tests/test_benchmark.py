"""Tests for competitor benchmarking (premium feature)."""
from app.core.database import SessionLocal
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


def test_benchmark_gated_for_free(auth_client):
    # Free plan lacks the "benchmarking" feature -> 402 upgrade required.
    assert auth_client.get("/api/v1/benchmark").status_code == 402


def test_premium_can_benchmark_competitors(auth_client):
    _set_plan("t@test.com", "premium")

    # Add a competitor.
    r = auth_client.post("/api/v1/benchmark/competitors", json={"name": "Rival Corp"})
    assert r.status_code == 201
    assert r.json()["name"] == "Rival Corp"

    assert len(auth_client.get("/api/v1/benchmark/competitors").json()) == 1

    # Report includes the user (is_you) plus the competitor.
    r = auth_client.get("/api/v1/benchmark")
    assert r.status_code == 200
    report = r.json()
    assert "generated_at" in report
    entries = report["entries"]
    assert len(entries) == 2

    you = entries[0]
    assert you["is_you"] is True
    assert 0.0 <= you["reputation_score"] <= 100.0
    assert set(you["sentiment"]) == {"positive", "neutral", "negative"}

    rival = entries[1]
    assert rival["is_you"] is False
    assert rival["name"] == "Rival Corp"
    # The offline demo connector synthesizes mentions, so the rival has data.
    assert rival["total_mentions"] > 0


def test_competitor_cap_enforced(auth_client):
    _set_plan("t@test.com", "premium")
    for i in range(5):
        assert auth_client.post(
            "/api/v1/benchmark/competitors", json={"name": f"Rival {i}"}
        ).status_code == 201
    # The 6th exceeds the per-user cap.
    assert auth_client.post(
        "/api/v1/benchmark/competitors", json={"name": "Rival 6"}
    ).status_code == 402


def test_competitor_delete_ownership(auth_client):
    _set_plan("t@test.com", "premium")
    cid = auth_client.post(
        "/api/v1/benchmark/competitors", json={"name": "Deletable"}
    ).json()["id"]
    assert auth_client.delete(f"/api/v1/benchmark/competitors/{cid}").status_code == 204
    # Unknown id -> 404.
    assert auth_client.delete("/api/v1/benchmark/competitors/does-not-exist").status_code == 404
