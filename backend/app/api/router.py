"""Aggregates every route module into one versioned API router."""
from __future__ import annotations

from fastapi import APIRouter

from .routes import (
    accounts,
    ai_visibility,
    alerts,
    analyze,
    auth,
    auth_extra,
    benchmark,
    billing,
    cleanup,
    cleanup_auto,
    dashboard,
    mentions,
    organizations,
    privacy,
    reports,
    scans,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(auth_extra.router)  # must follow auth.router (shared /auth prefix)
api_router.include_router(accounts.router)
api_router.include_router(scans.router)
api_router.include_router(mentions.router)
api_router.include_router(analyze.router)
api_router.include_router(ai_visibility.router)
api_router.include_router(dashboard.router)
api_router.include_router(alerts.router)
api_router.include_router(cleanup.router)
api_router.include_router(cleanup_auto.router)  # must follow cleanup.router (shared /cleanup prefix)
api_router.include_router(reports.router)
api_router.include_router(privacy.router)
api_router.include_router(billing.router)
api_router.include_router(benchmark.router)
api_router.include_router(organizations.router)
