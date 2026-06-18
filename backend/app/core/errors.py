"""Centralized error handling.

A catch-all handler for *unhandled* exceptions: it logs the full traceback with
the request's correlation id and returns a clean, consistent JSON body. In
production the response never leaks internal details; outside production the
exception message is included to speed up debugging.

FastAPI's own ``HTTPException`` / ``RequestValidationError`` handlers are left
untouched — those already produce safe, intentional responses. This only catches
the unexpected.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings

logger = logging.getLogger("noyou.errors")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log an unexpected error and return a sanitized ``500`` response.

    The correlation id (set by ``RequestIDMiddleware``) is logged and echoed in
    the body so a user-reported error id maps to exactly one log entry.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "Unhandled exception on %s %s (request_id=%s): %s",
        request.method,
        request.url.path,
        request_id,
        exc,
        exc_info=exc,
    )

    body: dict[str, object] = {"detail": "Internal server error"}
    if request_id:
        body["request_id"] = request_id
    # Surface the message only outside production — never leak internals to
    # end users in a production deployment.
    if settings.environment != "production":
        body["error"] = str(exc)

    return JSONResponse(status_code=500, content=body)


def register_error_handlers(app: FastAPI) -> None:
    """Install the catch-all exception handler on ``app``."""
    app.add_exception_handler(Exception, unhandled_exception_handler)
