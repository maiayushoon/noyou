"""Rate limiting via slowapi.

A single shared :data:`limiter` enforces a global per-client default (driven by
``settings.rate_limit_per_minute``). Sensitive endpoints — login, registration,
password reset — opt into the tighter :data:`AUTH_LIMIT` with the
``@limiter.limit(AUTH_LIMIT)`` decorator on the route.

Clients are identified by remote address (``get_remote_address``). Behind a proxy
you'll want the proxy to set a trusted forwarding header; the default keeps things
simple and safe for the single-host deployment NoYou ships with.

Wiring is centralized in :func:`register_rate_limiting`, called once from
``app.main``.
"""
from __future__ import annotations

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .config import settings

# Global limiter. ``default_limits`` applies to every route unless a route
# overrides it with its own ``@limiter.limit(...)`` decorator.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)

#: Tighter limit string for auth-sensitive endpoints (login/register/reset).
#: Apply per-route with ``@limiter.limit(AUTH_LIMIT)``.
AUTH_LIMIT = f"{settings.auth_rate_limit_per_minute}/minute"


def register_rate_limiting(app: FastAPI) -> None:
    """Attach the shared limiter, middleware, and 429 handler to ``app``.

    slowapi reads the limiter off ``app.state.limiter`` from inside the
    middleware, so that assignment must happen before the middleware runs. The
    ``RateLimitExceeded`` handler renders a clean JSON ``429`` with the
    standard ``Retry-After`` / ``X-RateLimit-*`` headers.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
