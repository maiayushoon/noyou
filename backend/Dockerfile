# ─────────────────────────────────────────────────────────────────────────────
# NoYou API — production image.
# Build context is the backend/ directory:  docker build -t noyou-api ./backend
# Served by gunicorn managing uvicorn workers (async ASGI) behind the container.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    WEB_CONCURRENCY=4

WORKDIR /app

# System deps for psycopg2 / bcrypt build (slim image). Build toolchain is only
# needed at install time, so it's removed in the same layer to keep the image lean.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so the layer caches across source-only changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application source.
COPY . .

# Run as a non-root user (defence in depth). /data is the mount point for the
# SQLite volume in docker-compose; create it up front owned by appuser so a fresh
# named volume inherits that ownership and the app can write noyou.db.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data
USER appuser

EXPOSE 8000

# Liveness probe — hits the unauthenticated /health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/health" || exit 1

# gunicorn process manager + uvicorn ASGI workers. WEB_CONCURRENCY controls the
# worker count (override per host: ~ 2 * vCPU + 1). The lifespan hook creates
# tables/seed and starts the scheduler in each worker as today; for multi-worker
# Postgres deployments run `alembic upgrade head` as a separate step (see DEPLOY.md).
CMD ["sh", "-c", "exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WEB_CONCURRENCY} \
    --bind 0.0.0.0:${PORT} \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -"]
