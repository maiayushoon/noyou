"""Tests for the Stripe billing backend.

These tests are deliberately independent of real Stripe keys and the network:
pure-logic helpers are exercised directly, the ``is_configured`` 503 paths are
asserted with billing unconfigured (the test env ships no Stripe keys), and the
one place that would call Stripe (the webhook) is monkeypatched so we test the
route's error handling without the SDK or a live signature.
"""
from types import SimpleNamespace

import pytest

from app.core.database import SessionLocal
from app.models.user import User
from app.services import billing


@pytest.fixture(autouse=True)
def _ensure_billing_router():
    """Make sure the billing routes are mounted for these tests.

    Production wires this via the build manifest's ``router_include`` (an
    ``api_router.include_router(billing.router)`` line in ``api/router.py``).
    When that change isn't present in the test environment yet, mount it here so
    the route tests exercise the real router. Idempotent: skips if already
    mounted.
    """
    from app.api.routes import billing as billing_routes
    from app.main import app

    already = any(getattr(r, "path", "").startswith("/api/v1/billing") for r in app.routes)
    if not already:
        app.include_router(billing_routes.router, prefix="/api/v1")
    yield


def _fake_settings(**overrides):
    """A settings stand-in for the price/plan helpers.

    The real ``Settings`` (pydantic) forbids assigning fields it doesn't declare,
    and the Stripe price fields are added to ``config.py`` via the build manifest
    (not necessarily present in this test environment). Patching ``billing.settings``
    with a plain namespace lets the pure-logic tests run regardless.
    """
    defaults = {
        "stripe_secret_key": "",
        "stripe_publishable_key": "",
        "stripe_price_pro": "",
        "stripe_price_premium": "",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


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


# --- Auth gating -------------------------------------------------------------
def test_checkout_requires_auth(client):
    # No bearer token -> 401 before any billing logic runs.
    r = client.post("/api/v1/billing/checkout", json={"plan": "pro"})
    assert r.status_code == 401


def test_portal_requires_auth(client):
    r = client.post("/api/v1/billing/portal")
    assert r.status_code == 401


def test_status_requires_auth(client):
    r = client.get("/api/v1/billing")
    assert r.status_code == 401


# --- Billing status ----------------------------------------------------------
def test_billing_status_for_free_user(auth_client):
    r = auth_client.get("/api/v1/billing")
    assert r.status_code == 200
    body = r.json()
    assert body["plan"] == "free"
    assert body["subscription_status"] is None
    assert body["has_active_subscription"] is False
    # No Stripe key configured in the test environment.
    assert body["publishable_key"] is None


def test_billing_status_reflects_plan(auth_client):
    _set_plan("t@test.com", "pro")
    r = auth_client.get("/api/v1/billing")
    assert r.status_code == 200
    assert r.json()["plan"] == "pro"


# --- Checkout validation / 503 -----------------------------------------------
def test_checkout_unconfigured_returns_503(auth_client):
    # Stripe isn't configured in tests, so even a valid plan hits the 503 guard.
    assert billing.is_configured() is False
    r = auth_client.post("/api/v1/billing/checkout", json={"plan": "pro"})
    assert r.status_code == 503


def test_checkout_rejects_invalid_plan(auth_client, monkeypatch):
    # Pretend billing is configured so we reach the plan validation, then assert
    # an unknown plan is rejected with 400 (never reaching Stripe).
    monkeypatch.setattr(billing, "is_configured", lambda: True)
    r = auth_client.post("/api/v1/billing/checkout", json={"plan": "free"})
    assert r.status_code == 400
    r = auth_client.post("/api/v1/billing/checkout", json={"plan": "enterprise"})
    assert r.status_code == 400


def test_portal_unconfigured_returns_503(auth_client):
    r = auth_client.post("/api/v1/billing/portal")
    assert r.status_code == 503


# --- Webhook -----------------------------------------------------------------
def test_webhook_bad_signature_returns_400(client, monkeypatch):
    """A bogus signature -> the service raises ValueError -> route returns 400.

    We monkeypatch ``handle_webhook`` to raise ``ValueError`` (exactly what a
    signature-verification failure does) so the test never needs the stripe SDK
    or a real signing secret.
    """

    def _boom(db, payload, sig):  # noqa: ANN001 - test stub
        raise ValueError("Invalid webhook signature")

    monkeypatch.setattr(billing, "handle_webhook", _boom)
    r = client.post(
        "/api/v1/billing/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={"stripe-signature": "t=1,v1=deadbeef"},
    )
    assert r.status_code == 400


def test_webhook_success_returns_received(client, monkeypatch):
    """When the service accepts the event, the route returns {received: True}."""

    def _ok(db, payload, sig):  # noqa: ANN001 - test stub
        return None

    monkeypatch.setattr(billing, "handle_webhook", _ok)
    r = client.post(
        "/api/v1/billing/webhook",
        content=b'{"type": "customer.subscription.updated"}',
        headers={"stripe-signature": "t=1,v1=whatever"},
    )
    assert r.status_code == 200
    assert r.json() == {"received": True}


# --- Pure-logic price/plan mapping -------------------------------------------
def test_price_for_plan_mapping(monkeypatch):
    monkeypatch.setattr(
        billing,
        "settings",
        _fake_settings(stripe_price_pro="price_pro_123", stripe_price_premium="price_prem_456"),
    )

    assert billing.price_for_plan("pro") == "price_pro_123"
    assert billing.price_for_plan("PREMIUM") == "price_prem_456"  # case-insensitive
    assert billing.price_for_plan("free") is None
    assert billing.price_for_plan("nonsense") is None


def test_plan_for_price_mapping(monkeypatch):
    monkeypatch.setattr(
        billing,
        "settings",
        _fake_settings(stripe_price_pro="price_pro_123", stripe_price_premium="price_prem_456"),
    )

    assert billing.plan_for_price("price_pro_123") == "pro"
    assert billing.plan_for_price("price_prem_456") == "premium"
    # Unknown / missing prices fall back to free (never silently grant a tier).
    assert billing.plan_for_price("price_unknown") == "free"
    assert billing.plan_for_price(None) == "free"


def test_round_trip_price_plan(monkeypatch):
    monkeypatch.setattr(
        billing,
        "settings",
        _fake_settings(stripe_price_pro="price_pro_123", stripe_price_premium="price_prem_456"),
    )

    for plan in ("pro", "premium"):
        assert billing.plan_for_price(billing.price_for_plan(plan)) == plan
