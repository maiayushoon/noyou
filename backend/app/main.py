"""NoYou API — application entrypoint.

Run with:  uvicorn app.main:app --reload   (from the backend/ directory)
Serves the JSON API under /api/v1 and the dashboard UI at /.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .api.router import api_router
from .core.config import settings
from .core.database import Base, SessionLocal, engine
from .core.errors import register_error_handlers
from .core.middleware import register_security
from .core.ratelimit import register_rate_limiting
from .core.scheduler import shutdown_scheduler, start_scheduler
from .core.seed import seed_demo

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("noyou")

# Note: SECRET_KEY strength is enforced in core/config.py:get_settings() — it
# auto-generates an ephemeral key in development and refuses to boot in any other
# environment unless a strong, unique secret is supplied.
_IS_PROD = settings.environment == "production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models so every table is registered on Base before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_demo(db)
    finally:
        db.close()

    start_scheduler()
    logger.info("%s v%s ready (env=%s)", settings.project_name, __version__, settings.environment)
    yield
    shutdown_scheduler()


app = FastAPI(
    title=f"{settings.project_name} — Digital Reputation API",
    version=__version__,
    description="AI-powered digital identity & reputation management.",
    lifespan=lifespan,
    # Hide interactive docs / schema in production to reduce attack surface.
    docs_url=None if _IS_PROD else "/docs",
    redoc_url=None if _IS_PROD else "/redoc",
    openapi_url=None if _IS_PROD else "/openapi.json",
)

# Order matters: register security + rate limiting + error handling before CORS so
# CORS stays the outermost middleware layer (Starlette runs middleware in reverse).
register_security(app)          # security headers + X-Request-ID
register_rate_limiting(app)     # slowapi limiter + 429 handler + middleware
register_error_handlers(app)    # sanitized catch-all 500 handler

# CORS. In development, allow ANY localhost/127.0.0.1 port — Next.js dev hops to
# 3000/3001/3002/... whenever a port is taken, so a fixed list keeps breaking.
# In production only the explicit CORS_ORIGINS list is honored.
_cors_regex = (
    r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
    if settings.environment == "development"
    else None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=_cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "service": settings.project_name, "version": __version__}


# API-only. The user-facing UI is the standalone Next.js app in ../frontend
# (served separately on its own host); this server exposes only the JSON API.
@app.get("/", include_in_schema=False)
def root():
    return {
        "service": settings.project_name,
        "status": "ok",
        "docs": "/docs",
        "api": settings.api_v1_prefix,
        "app": settings.frontend_url,
    }
