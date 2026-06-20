"""API + connector tests for the Connections (OAuth account-linking) feature.

These use the shared ``client`` / ``auth_client`` fixtures and a ``_set_plan``
helper (matching ``test_prod_features.py``) to promote the test user, since every
connection endpoint is gated behind a paid plan. They stay hermetic: the only
provider behavior exercised at runtime is the owned-content connector with NO linked
accounts (so it never reaches the network) and the DELETE ownership check (which
404s before any upstream revoke).
"""
from __future__ import annotations

from app.core.crypto import encrypt_token
from app.core.database import SessionLocal
from app.models.linked_account import LinkedAccount
from app.models.user import User
from app.schemas.connection import ConnectionOut


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


def _user_id(email: str) -> str:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first().id
    finally:
        db.close()


def _make_linked_account(user_id: str, provider: str = "reddit") -> str:
    """Insert a connected LinkedAccount for ``user_id`` and return its id."""
    db = SessionLocal()
    try:
        linked = LinkedAccount(
            user_id=user_id,
            provider=provider,
            external_id=f"ext-{user_id[:8]}",
            external_handle="someone",
            status="connected",
            access_token_enc=encrypt_token("access-token"),
        )
        db.add(linked)
        db.commit()
        db.refresh(linked)
        return linked.id
    finally:
        db.close()


# --- plan gating -------------------------------------------------------------
def test_providers_requires_paid_plan(auth_client):
    # Free user is rejected with 402 (upgrade required).
    assert auth_client.get("/api/v1/connections/providers").status_code == 402


def test_providers_listed_for_paid_plan(auth_client):
    _set_plan("t@test.com", "pro")
    r = auth_client.get("/api/v1/connections/providers")
    assert r.status_code == 200
    body = r.json()
    names = {p["provider"] for p in body}
    assert names == {"mastodon", "youtube", "reddit", "threads", "instagram"}
    # Mastodon is always configured; the keyed providers are not (no creds in tests).
    by_name = {p["provider"]: p for p in body}
    assert by_name["mastodon"]["configured"] is True
    assert by_name["reddit"]["configured"] is False
    # Scopes are surfaced as a list for the consent transparency UI.
    assert isinstance(by_name["reddit"]["scopes_requested"], list)
    assert by_name["reddit"]["scopes_requested"]  # non-empty


def test_list_connections_requires_paid_plan(auth_client):
    assert auth_client.get("/api/v1/connections").status_code == 402


def test_list_connections_empty_for_paid_user(auth_client):
    _set_plan("t@test.com", "pro")
    r = auth_client.get("/api/v1/connections")
    assert r.status_code == 200
    assert r.json() == []


def test_connect_unknown_provider_is_404(auth_client):
    _set_plan("t@test.com", "pro")
    r = auth_client.post("/api/v1/connections/nope/connect", json={})
    assert r.status_code == 404


def test_connect_unconfigured_provider_is_400(auth_client):
    # Reddit has no app creds in tests -> connect cannot start.
    _set_plan("t@test.com", "pro")
    r = auth_client.post("/api/v1/connections/reddit/connect", json={})
    assert r.status_code == 400


# --- ConnectionOut never leaks token material --------------------------------
def test_connection_out_excludes_token_fields():
    # The serializer must not have, and must not emit, the encrypted token columns.
    fields = set(ConnectionOut.model_fields)
    assert "access_token_enc" not in fields
    assert "refresh_token_enc" not in fields

    out = ConnectionOut(
        id="1",
        provider="reddit",
        status="connected",
        scopes="identity history read",
        created_at="2026-01-01T00:00:00Z",
    )
    dumped = out.model_dump()
    assert "access_token_enc" not in dumped
    assert "refresh_token_enc" not in dumped
    # The space-delimited scope string is exposed as a list.
    assert dumped["scopes"] == ["identity", "history", "read"]


def test_list_connections_response_has_no_token_fields(auth_client):
    _set_plan("t@test.com", "pro")
    uid = _user_id("t@test.com")
    _make_linked_account(uid)
    r = auth_client.get("/api/v1/connections")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert "access_token_enc" not in rows[0]
    assert "refresh_token_enc" not in rows[0]


# --- owned-content connector with no accounts --------------------------------
def test_owned_connector_no_accounts_is_unconfigured_and_empty():
    from app.connectors.owned import OwnedContentConnector

    db = SessionLocal()
    try:
        user = User(
            email="owned@test.com", full_name="Owned", password_hash="x", plan="pro"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        connector = OwnedContentConnector(db, user)
        # No linked accounts -> not usable, and search never raises / never hits net.
        assert connector.is_configured() is False
        assert connector.search("anything") == []
        # Idempotent: still empty on a second call.
        assert connector.search("anything") == []
    finally:
        db.close()


# --- DELETE ownership checks -------------------------------------------------
def test_delete_connection_requires_paid_plan(auth_client):
    # Free user can't even reach the ownership check.
    import uuid

    assert (
        auth_client.delete(f"/api/v1/connections/{uuid.uuid4()}").status_code == 402
    )


def test_delete_nonexistent_connection_is_404(auth_client):
    import uuid

    _set_plan("t@test.com", "pro")
    r = auth_client.delete(f"/api/v1/connections/{uuid.uuid4()}")
    assert r.status_code == 404


def test_delete_malformed_id_is_404(auth_client):
    _set_plan("t@test.com", "pro")
    # A non-UUID path param must 404 cleanly (not 500 on a UUID column).
    assert auth_client.delete("/api/v1/connections/not-a-uuid").status_code == 404


def test_delete_other_users_connection_is_404(auth_client):
    # Set up a SECOND user who owns a linked account, then try to delete it as the
    # authenticated (first) user — ownership check must 404, not delete it.
    _set_plan("t@test.com", "pro")

    db = SessionLocal()
    try:
        other = User(
            email="other@test.com", full_name="Other", password_hash="x", plan="pro"
        )
        db.add(other)
        db.commit()
        db.refresh(other)
        other_id = other.id
    finally:
        db.close()

    linked_id = _make_linked_account(other_id)

    r = auth_client.delete(f"/api/v1/connections/{linked_id}")
    assert r.status_code == 404

    # And the row still exists (it was NOT deleted by a non-owner).
    db = SessionLocal()
    try:
        assert db.get(LinkedAccount, linked_id) is not None
    finally:
        db.close()


def test_delete_own_connection_succeeds(auth_client):
    _set_plan("t@test.com", "pro")
    uid = _user_id("t@test.com")
    # Use mastodon so the best-effort revoke is a no-op with no cached app (no network).
    linked_id = _make_linked_account(uid, provider="mastodon")

    r = auth_client.delete(f"/api/v1/connections/{linked_id}")
    assert r.status_code == 204

    db = SessionLocal()
    try:
        assert db.get(LinkedAccount, linked_id) is None
    finally:
        db.close()
