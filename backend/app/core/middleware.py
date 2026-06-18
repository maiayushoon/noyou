"""HTTP security middleware.

Two cross-cutting concerns that belong on every response:

* :class:`SecurityHeadersMiddleware` — hardens the browser surface (clickjacking,
  MIME sniffing, referrer leakage) and ships a Content-Security-Policy tuned for
  the zero-build frontend, which loads Tailwind/Alpine from public CDNs.
* :class:`RequestIDMiddleware` — stamps every response with a unique
  ``X-Request-ID`` so a log line can be tied back to a specific request (the
  error handler echoes the same id).

Both are registered once via :func:`register_security` from ``app.main``.
"""
from __future__ import annotations

import uuid

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from .config import settings

#: Header used to read/propagate the per-request correlation id.
REQUEST_ID_HEADER = "X-Request-ID"

# Content-Security-Policy for the dashboard. The frontend pulls Tailwind and
# Alpine from CDNs and both require inline styles/scripts, so we explicitly
# allow the known-good origins plus 'unsafe-inline'/'unsafe-eval'. Everything
# else falls back to 'self'. Kept as one place so the policy is auditable.
_CSP = "; ".join(
    [
        "default-src 'self'",
        (
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.tailwindcss.com https://cdn.jsdelivr.net"
        ),
        (
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://fonts.googleapis.com"
        ),
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:",
        "img-src 'self' data: https:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
)

# Static headers applied to every response regardless of environment.
_STATIC_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": _CSP,
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add hardening headers (and HSTS in production) to every response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # Don't clobber a header a handler may have set deliberately.
        for header, value in _STATIC_SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)

        # HSTS is only meaningful (and safe) over HTTPS in production; enabling
        # it during local HTTP development would pin browsers to https://localhost.
        if settings.environment == "production":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a correlation id to every request and echo it on the response.

    Honors an inbound ``X-Request-ID`` (so an upstream proxy/gateway id is
    preserved) and otherwise mints a fresh UUID4. The id is stored on
    ``request.state.request_id`` for downstream handlers and the error handler.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def register_security(app: FastAPI) -> None:
    """Register the security-header and request-id middleware on ``app``.

    ``RequestIDMiddleware`` is added last so it runs first (Starlette executes
    middleware in reverse registration order), guaranteeing every response —
    including those produced by the security middleware — carries a request id.
    """
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
