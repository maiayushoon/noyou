"""Pytest fixtures: isolated in-memory app + authenticated client.

Each test run uses a fresh SQLite file and disables the scheduler/seed so tests are
fast and deterministic.
"""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_noyou.db")
os.environ["SEED_DEMO"] = "false"
os.environ["SCAN_INTERVAL_MINUTES"] = "0"
os.environ["SECRET_KEY"] = "test-secret"
# Pin tests to the offline connector + analyzer regardless of any backend/.env,
# so the suite never makes real network calls (env vars beat the .env file).
os.environ["CONNECTORS"] = "demo"
os.environ["ANALYZER"] = "rule_based"
# Effectively disable rate limiting in tests — every TestClient request shares one
# client IP, so real limits would spuriously 429 the suite.
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000000"
os.environ["AUTH_RATE_LIMIT_PER_MINUTE"] = "1000000"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_client(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "t@test.com", "password": "password123", "full_name": "Test User"},
    )
    token = client.post(
        "/api/v1/auth/login", json={"email": "t@test.com", "password": "password123"}
    ).json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
