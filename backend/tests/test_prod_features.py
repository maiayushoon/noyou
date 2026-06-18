"""Tests for the production features: plan gating, quotas, predictive, auth flows, GDPR."""
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


# --- Plan gating -------------------------------------------------------------
def test_free_plan_account_limit(auth_client):
    # Free plan allows exactly 1 monitored identity.
    r1 = auth_client.post("/api/v1/accounts", json={"platform": "google", "handle": "One"})
    assert r1.status_code == 201
    r2 = auth_client.post("/api/v1/accounts", json={"platform": "google", "handle": "Two"})
    assert r2.status_code == 402


def test_free_plan_scan_quota(auth_client):
    # Free plan allows 3 scans/day; the 4th is rejected with 429.
    for _ in range(3):
        assert auth_client.post("/api/v1/scans").status_code == 202
    assert auth_client.post("/api/v1/scans").status_code == 429


def test_predictive_gated_for_free(auth_client):
    r = auth_client.post("/api/v1/analyze", json={"text": "I love this product, it is amazing!"})
    assert r.status_code == 402  # Pro feature


def test_predictive_works_for_pro(auth_client):
    _set_plan("t@test.com", "pro")
    r = auth_client.post(
        "/api/v1/analyze",
        json={"text": "My manager is incompetent and this company is a fraud."},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["publish_recommendation"] in ("safe_to_post", "review_suggested", "do_not_post")
    assert body["sentiment"] == "negative"
    assert body["publish_recommendation"] == "do_not_post"


def test_predictive_safe_post(auth_client):
    _set_plan("t@test.com", "pro")
    r = auth_client.post(
        "/api/v1/analyze",
        json={"text": "Grateful to my team for an excellent, inspiring launch today!"},
    )
    assert r.json()["publish_recommendation"] == "safe_to_post"


# --- Auth flows --------------------------------------------------------------
def test_forgot_password_is_enumeration_safe(client):
    # Unknown email still returns a generic 200 (no account enumeration).
    r = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@nowhere.com"})
    assert r.status_code == 200
    assert "message" in r.json()


def test_reset_password_bad_token(client):
    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "definitely-not-valid", "new_password": "newpassword123"},
    )
    assert r.status_code == 400


def test_verify_email_bad_token(client):
    r = client.post("/api/v1/auth/verify-email", json={"token": "nope"})
    assert r.status_code == 400


def test_password_reset_end_to_end(client):
    """Register, mint a reset token via the service, reset, then log in with it."""
    client.post("/api/v1/auth/register", json={"email": "reset@test.com", "password": "oldpassword1"})

    from app.models.user import User as U
    from app.services.account_email import PURPOSE_RESET, create_token

    db = SessionLocal()
    try:
        user = db.query(U).filter(U.email == "reset@test.com").first()
        token = create_token(db, user, PURPOSE_RESET).token
    finally:
        db.close()

    r = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "brandnewpass1"}
    )
    assert r.status_code == 200
    # Old password rejected, new one works.
    assert client.post("/api/v1/auth/login", json={"email": "reset@test.com", "password": "oldpassword1"}).status_code == 400
    assert client.post("/api/v1/auth/login", json={"email": "reset@test.com", "password": "brandnewpass1"}).status_code == 200

    # A reset token is single-use.
    assert client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "another1pass"}
    ).status_code == 400


# --- GDPR --------------------------------------------------------------------
def test_data_export(auth_client):
    auth_client.post("/api/v1/accounts", json={"platform": "google", "handle": "Exporter"})
    auth_client.post("/api/v1/scans")
    r = auth_client.get("/api/v1/privacy/export")
    assert r.status_code == 200
    body = r.json()
    assert body["profile"]["email"] == "t@test.com"
    assert "password_hash" not in body["profile"]  # secrets never exported
    assert body["counts"]["mentions"] >= 0
    assert "accounts" in body and "scans" in body


def test_account_deletion_erases_everything(client):
    client.post("/api/v1/auth/register", json={"email": "del@test.com", "password": "password123"})
    token = client.post(
        "/api/v1/auth/login", json={"email": "del@test.com", "password": "password123"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/accounts", json={"platform": "google", "handle": "Doomed"}, headers=headers)
    client.post("/api/v1/scans", headers=headers)

    assert client.delete("/api/v1/privacy/account", headers=headers).status_code == 204
    # Token no longer resolves to a user.
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


# --- Real connectors registry ------------------------------------------------
def test_keyless_connectors_registered():
    from app.connectors.registry import get_connector

    for name in ("web", "hackernews", "reddit_public"):
        conn = get_connector(name)
        assert conn is not None
        assert conn.is_configured() is True


# --- Security fixes ----------------------------------------------------------
def test_token_revoked_after_password_change(client):
    """An access token issued before a password change is rejected (session revocation)."""
    from datetime import datetime, timedelta, timezone

    from app.models.user import User as U

    client.post("/api/v1/auth/register", json={"email": "rev@test.com", "password": "oldpassword1"})
    token = client.post(
        "/api/v1/auth/login", json={"email": "rev@test.com", "password": "oldpassword1"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    # Simulate a later password change (clearly after the token's iat).
    db = SessionLocal()
    try:
        user = db.query(U).filter(U.email == "rev@test.com").first()
        user.password_changed_at = datetime.now(timezone.utc) + timedelta(seconds=30)
        db.add(user)
        db.commit()
    finally:
        db.close()

    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_external_urls_are_scheme_sanitized():
    """javascript:/data: URLs from scraped content are dropped on ingest."""
    from app.services.scanning import _safe_url

    assert _safe_url("https://example.com/x") == "https://example.com/x"
    assert _safe_url("http://example.com") == "http://example.com"
    assert _safe_url("javascript:alert(1)") is None
    assert _safe_url("data:text/html,<script>1</script>") is None
    assert _safe_url(None) is None


def test_free_plan_only_uses_allowed_connectors():
    """A free user's scan must not use keyed/paid connectors."""
    from app.core.plans import plan_allows_connector

    assert plan_allows_connector("free", "web") is True
    assert plan_allows_connector("free", "hackernews") is True
    assert plan_allows_connector("free", "google") is False   # paid connector
    assert plan_allows_connector("free", "twitter") is False
    assert plan_allows_connector("premium", "google") is True  # "all"
