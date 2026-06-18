"""Gunicorn configuration for running NoYou in production.

Gunicorn is the process manager / master; each worker is a Uvicorn worker that
actually speaks ASGI to the FastAPI app. This combo gives us battle-tested
process supervision (graceful restarts, worker recycling) plus async I/O.

Run with:
    gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py

Every value below can be overridden via an environment variable so the same
image works for a small VPS and a larger box without rebuilding. See
``.env.production.example`` and ``DEPLOYMENT.md`` for guidance and the scaling
notes (notably: when running more than one *instance*, move the in-process
APScheduler to an external worker so scans don't double-run).
"""
from __future__ import annotations

import multiprocessing
import os


def _int_env(name: str, default: int) -> int:
    """Read an int from the environment, falling back on any bad/empty value."""
    raw = os.getenv(name, "")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


# --- Networking ---
# Bind inside the container; Caddy (or the platform's router) terminates TLS in
# front of us and reverse-proxies plain HTTP to this port.
_host = os.getenv("GUNICORN_HOST", "0.0.0.0")
_port = os.getenv("PORT") or os.getenv("GUNICORN_PORT", "8000")
bind = f"{_host}:{_port}"

# --- Workers ---
# Default to the common (2 * CPU) + 1 heuristic, but let WEB_CONCURRENCY /
# GUNICORN_WORKERS pin it explicitly (recommended on shared/small hosts).
_default_workers = (multiprocessing.cpu_count() * 2) + 1
workers = _int_env("WEB_CONCURRENCY", 0) or _int_env("GUNICORN_WORKERS", _default_workers)

# UvicornWorker turns each Gunicorn worker into an ASGI server for FastAPI.
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")

# Cap concurrent connections per worker (UvicornWorker honours this).
worker_connections = _int_env("GUNICORN_WORKER_CONNECTIONS", 1000)

# --- Timeouts ---
# A scan/report request can take a little while; keep the worker timeout
# comfortably above any single request. Keep-alive matches typical proxy idle.
timeout = _int_env("GUNICORN_TIMEOUT", 120)
graceful_timeout = _int_env("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _int_env("GUNICORN_KEEPALIVE", 5)

# --- Worker recycling ---
# Recycle workers periodically to bound the impact of any slow memory leak.
# The jitter avoids all workers restarting at the same instant.
max_requests = _int_env("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = _int_env("GUNICORN_MAX_REQUESTS_JITTER", 100)

# --- Logging ---
# "-" sends access and error logs to stdout/stderr, which is what container
# log collectors (docker logs, Render, Fly) expect. Set GUNICORN_ACCESS_LOG=""
# to disable access logging on very chatty deployments.
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
# Add the response time (%(D)s, in microseconds) to the default access format.
access_log_format = os.getenv(
    "GUNICORN_ACCESS_LOG_FORMAT",
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sus',
)

# --- Process naming / misc ---
proc_name = os.getenv("GUNICORN_PROC_NAME", "noyou")
# Use /dev/shm for the heartbeat file when available to avoid disk-stall hangs.
worker_tmp_dir = "/dev/shm" if os.path.isdir("/dev/shm") else None
# Trust the X-Forwarded-* headers from the reverse proxy (Caddy) on all hops.
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
