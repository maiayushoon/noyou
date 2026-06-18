"""Tests for automated cleanup execution (Pro+ feature)."""
from app.core.database import SessionLocal
from app.models.analysis import Analysis
from app.models.cleanup import CleanupAction
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


def _seed_archive_action(email: str) -> tuple[str, str]:
    """Seed a mention + analysis + a 'suggested' archive cleanup action.

    Returns ``(mention_id, action_id)`` so the test can assert on them later.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        mention = Mention(
            user_id=user.id,
            source="reddit",
            external_id="seed-1",
            url="https://reddit.com/r/x/seed-1",
            title="A risky post about the user",
            content="Some negative content.",
            status="active",
        )
        db.add(mention)
        db.flush()
        db.add(
            Analysis(
                mention_id=mention.id,
                sentiment="negative",
                sentiment_score=-0.8,
                risk_level=4,
                risk_category="reputation",
                confidence=0.9,
            )
        )
        action = CleanupAction(
            user_id=user.id,
            mention_id=mention.id,
            action_type="archive",
            title="Archive this mention",
            instructions="Hide from your active dashboard once handled.",
            status="suggested",
        )
        db.add(action)
        db.commit()
        return mention.id, action.id
    finally:
        db.close()


def test_auto_execute_requires_paid_plan(auth_client):
    # Free user is gated out with 402 (upgrade required).
    r = auth_client.post("/api/v1/cleanup/auto-execute")
    assert r.status_code == 402


def test_auto_execute_archives_mention_for_pro(auth_client):
    _set_plan("t@test.com", "pro")
    mention_id, action_id = _seed_archive_action("t@test.com")

    r = auth_client.post("/api/v1/cleanup/auto-execute")
    assert r.status_code == 200
    body = r.json()
    assert body["executed"] >= 1
    assert body["dry_run"] is False

    # The archive action is completed and its mention is archived in the DB.
    db = SessionLocal()
    try:
        action = db.get(CleanupAction, action_id)
        assert action.status == "completed"
        mention = db.get(Mention, mention_id)
        assert mention.status == "archived"
    finally:
        db.close()


def test_auto_execute_dry_run_does_not_persist(auth_client):
    _set_plan("t@test.com", "pro")
    mention_id, action_id = _seed_archive_action("t@test.com")

    r = auth_client.post("/api/v1/cleanup/auto-execute?dry_run=true")
    assert r.status_code == 200
    body = r.json()
    assert body["dry_run"] is True
    assert body["executed"] >= 1

    # Nothing was actually mutated.
    db = SessionLocal()
    try:
        action = db.get(CleanupAction, action_id)
        assert action.status == "suggested"
        mention = db.get(Mention, mention_id)
        assert mention.status == "active"
    finally:
        db.close()
