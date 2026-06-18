"""Tests for the teams / organizations feature.

Independent of the build manifest being applied yet (mirrors test_billing.py):
- imports the Organization models at module scope so their tables register on
  ``Base`` before conftest's ``create_all`` runs, even if ``models/__init__.py``
  doesn't import them yet;
- mounts the orgs router in an autouse fixture if it isn't already mounted via
  ``api/router.py``.
"""
from __future__ import annotations

import pytest

from app.core.database import SessionLocal

# Import models at module scope so their tables are registered on Base.metadata
# before conftest's fresh_db fixture calls create_all().
from app.models.organization import Organization, OrganizationMember  # noqa: F401
from app.models.user import User

API = "/api/v1"


@pytest.fixture(autouse=True)
def _ensure_orgs_router():
    """Mount the orgs router if the manifest's router_include isn't applied yet."""
    from app.api.routes import organizations as orgs_routes
    from app.main import app

    already = any(getattr(r, "path", "").startswith(f"{API}/orgs") for r in app.routes)
    if not already:
        app.include_router(orgs_routes.router, prefix=API)
    yield


def _register(client, email: str, password: str = "password123") -> None:
    client.post(
        f"{API}/auth/register",
        json={"email": email, "password": password, "full_name": email.split("@")[0]},
    )


def _token(client, email: str, password: str = "password123") -> str:
    return client.post(
        f"{API}/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _auth_headers(client, email: str, password: str = "password123") -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(client, email, password)}"}


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


# --- Auth / plan gating ------------------------------------------------------
def test_create_org_requires_auth(client):
    r = client.post(f"{API}/orgs", json={"name": "Acme"})
    assert r.status_code == 401


def test_free_user_create_org_returns_402(client):
    _register(client, "free@test.com")
    headers = _auth_headers(client, "free@test.com")
    r = client.post(f"{API}/orgs", json={"name": "Acme"}, headers=headers)
    assert r.status_code == 402


# --- Full happy path ---------------------------------------------------------
def test_premium_user_creates_org_invites_and_member_views_dashboard(client):
    # Owner is premium; an invitee is already registered.
    _register(client, "owner@test.com")
    _set_plan("owner@test.com", "premium")
    _register(client, "member@test.com")

    owner_headers = _auth_headers(client, "owner@test.com")

    # Create the org.
    r = client.post(f"{API}/orgs", json={"name": "Acme Corp"}, headers=owner_headers)
    assert r.status_code == 201, r.text
    org = r.json()
    org_id = org["id"]
    assert org["name"] == "Acme Corp"
    assert org["role"] == "owner"

    # Invite the registered member by email -> linked + active immediately.
    r = client.post(
        f"{API}/orgs/{org_id}/members",
        json={"email": "member@test.com"},
        headers=owner_headers,
    )
    assert r.status_code == 201, r.text
    member = r.json()
    assert member["email"] == "member@test.com"
    assert member["status"] == "active"

    # The invited (registered) member sees the org in their list with member role.
    member_headers = _auth_headers(client, "member@test.com")
    r = client.get(f"{API}/orgs", headers=member_headers)
    assert r.status_code == 200
    orgs = r.json()
    assert len(orgs) == 1
    assert orgs[0]["id"] == org_id
    assert orgs[0]["role"] == "member"

    # The member can view the owner's dashboard (read-only) via the org.
    r = client.get(f"{API}/orgs/{org_id}/dashboard", headers=member_headers)
    assert r.status_code == 200
    body = r.json()
    assert "reputation_score" in body
    assert "sentiment_counts" in body

    # The owner can view their own org dashboard too.
    r = client.get(f"{API}/orgs/{org_id}/dashboard", headers=owner_headers)
    assert r.status_code == 200


# --- Access control ----------------------------------------------------------
def test_non_member_cannot_view_dashboard(client):
    _register(client, "owner2@test.com")
    _set_plan("owner2@test.com", "enterprise")
    _register(client, "stranger@test.com")

    owner_headers = _auth_headers(client, "owner2@test.com")
    org_id = client.post(
        f"{API}/orgs", json={"name": "Private Co"}, headers=owner_headers
    ).json()["id"]

    stranger_headers = _auth_headers(client, "stranger@test.com")
    r = client.get(f"{API}/orgs/{org_id}/dashboard", headers=stranger_headers)
    assert r.status_code == 403

    # A stranger also can't list the org's members.
    r = client.get(f"{API}/orgs/{org_id}/members", headers=stranger_headers)
    assert r.status_code == 403

    # A stranger sees no orgs in their own list.
    r = client.get(f"{API}/orgs", headers=stranger_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_only_owner_can_invite_and_remove(client):
    _register(client, "owner3@test.com")
    _set_plan("owner3@test.com", "premium")
    _register(client, "member3@test.com")

    owner_headers = _auth_headers(client, "owner3@test.com")
    org_id = client.post(
        f"{API}/orgs", json={"name": "Team Three"}, headers=owner_headers
    ).json()["id"]

    member_id = client.post(
        f"{API}/orgs/{org_id}/members",
        json={"email": "member3@test.com"},
        headers=owner_headers,
    ).json()["id"]

    # The member (not owner) cannot invite others.
    member_headers = _auth_headers(client, "member3@test.com")
    r = client.post(
        f"{API}/orgs/{org_id}/members",
        json={"email": "another@test.com"},
        headers=member_headers,
    )
    assert r.status_code == 403

    # The member cannot remove anyone.
    r = client.delete(f"{API}/orgs/{org_id}/members/{member_id}", headers=member_headers)
    assert r.status_code == 403

    # The owner can remove the member.
    r = client.delete(f"{API}/orgs/{org_id}/members/{member_id}", headers=owner_headers)
    assert r.status_code == 204


def test_invite_unregistered_email_stays_invited(client):
    _register(client, "owner4@test.com")
    _set_plan("owner4@test.com", "premium")

    owner_headers = _auth_headers(client, "owner4@test.com")
    org_id = client.post(
        f"{API}/orgs", json={"name": "Team Four"}, headers=owner_headers
    ).json()["id"]

    # Email with no matching user -> invited, not yet linked/active.
    r = client.post(
        f"{API}/orgs/{org_id}/members",
        json={"email": "ghost@test.com"},
        headers=owner_headers,
    )
    assert r.status_code == 201
    assert r.json()["status"] == "invited"
