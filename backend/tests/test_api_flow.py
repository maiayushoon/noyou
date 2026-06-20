"""End-to-end smoke test of the whole pipeline through the HTTP API.

Scans are async (POST returns 202 + a pending scan; work runs in a background task).
Under TestClient the background task completes during the POST call, so the final
state is available immediately via GET /scans/{id} — `_run_scan` fetches it.
"""


def _run_scan(client):
    """Trigger a scan and return its completed record."""
    scan = client.post("/api/v1/scans").json()
    return client.get(f"/api/v1/scans/{scan['id']}").json()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_login_me(client):
    assert client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "password123", "full_name": "A B"},
    ).status_code == 201
    token = client.post(
        "/api/v1/auth/login", json={"email": "a@b.com", "password": "password123"}
    ).json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "a@b.com"


def test_duplicate_register_rejected(client):
    client.post("/api/v1/auth/register", json={"email": "d@b.com", "password": "password123"})
    r = client.post("/api/v1/auth/register", json={"email": "d@b.com", "password": "password123"})
    assert r.status_code == 400


def test_unauthenticated_dashboard_rejected(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_full_scan_pipeline(auth_client):
    # Link an identity to scan for.
    auth_client.post("/api/v1/accounts", json={"platform": "google", "handle": "Jane Tester"})

    # Run a scan — demo connector should produce mentions + analysis.
    scan = _run_scan(auth_client)
    assert scan["status"] == "completed"
    assert scan["new_mentions"] > 0

    # Dashboard reflects the scan.
    dash = auth_client.get("/api/v1/dashboard").json()
    assert dash["total_mentions"] > 0
    assert 0 <= dash["reputation_score"] <= 100
    assert dash["band"] in ("excellent", "high", "medium", "low", "critical")

    # Mentions have analysis attached.
    mentions = auth_client.get("/api/v1/mentions").json()
    assert mentions and mentions[0]["analysis"] is not None

    # Cleanup suggestions were generated for risky items.
    cleanup = auth_client.get("/api/v1/cleanup").json()
    assert isinstance(cleanup, list)

    # Reports aggregate without error.
    report = auth_client.get("/api/v1/reports").json()
    assert "sentiment_distribution" in report


def test_mention_status_update_changes_score(auth_client):
    auth_client.post("/api/v1/accounts", json={"platform": "google", "handle": "Risky Person"})
    _run_scan(auth_client)
    before = auth_client.get("/api/v1/dashboard").json()["reputation_score"]

    # Archive every negative mention; score should not decrease.
    mentions = auth_client.get("/api/v1/mentions", params={"sentiment": "negative"}).json()
    for m in mentions:
        auth_client.patch(f"/api/v1/mentions/{m['id']}/status", json={"status": "removed"})

    after = auth_client.get("/api/v1/dashboard").json()["reputation_score"]
    assert after >= before


def test_rescan_dedupes(auth_client):
    auth_client.post("/api/v1/accounts", json={"platform": "google", "handle": "Same Person"})
    first = _run_scan(auth_client)
    second = _run_scan(auth_client)
    assert second["new_mentions"] == 0  # nothing new on identical re-scan
    assert first["new_mentions"] > 0
