"""Background scheduler — runs automated scans so the product is '24/7'.

Uses APScheduler's in-process BackgroundScheduler: no broker, no extra service,
perfect for a single-node deployment and trivially swappable for Celery/Cloud
schedulers at scale (see ROADMAP). Disabled when SCAN_INTERVAL_MINUTES=0.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from .config import settings
from .database import SessionLocal
from ..models.user import User

logger = logging.getLogger("noyou.scheduler")

_scheduler: BackgroundScheduler | None = None


def _scan_all_users() -> None:
    # Imported here to avoid a circular import at module load.
    from ..services.scanning import run_scan

    db = SessionLocal()
    try:
        users = db.scalars(select(User).where(User.is_active == True)).all()  # noqa: E712
        for user in users:
            try:
                run_scan(db, user, trigger="scheduled")
            except Exception:
                logger.exception("scheduled scan failed for user %s", user.id)
    finally:
        db.close()


def _send_weekly_digests() -> None:
    """Scheduled job: email each active user their weekly reputation digest.

    Self-contained and defensive — opens its own session and never propagates an
    exception into the scheduler thread. send_weekly_digests itself isolates each
    user and respects settings.digest_enabled.
    """
    # Imported here to avoid a circular import at module load.
    from ..services.digest import send_weekly_digests

    db = SessionLocal()
    try:
        send_weekly_digests(db)
    except Exception:
        logger.exception("weekly digest job failed")
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    scan_enabled = settings.scan_interval_minutes > 0
    digest_enabled = settings.digest_enabled

    # Nothing to run — don't spin up a scheduler thread at all.
    if not scan_enabled and not digest_enabled:
        logger.info("Scheduler disabled (no periodic scan and no weekly digest)")
        return None
    if _scheduler and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(daemon=True)

    if scan_enabled:
        _scheduler.add_job(
            _scan_all_users,
            "interval",
            minutes=settings.scan_interval_minutes,
            id="periodic_scan",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    if digest_enabled:
        # Weekly cron job. coalesce + max_instances=1 + replace_existing keep it
        # idempotent across restarts (no pile-up, no duplicate registration).
        _scheduler.add_job(
            _send_weekly_digests,
            "cron",
            day_of_week=settings.weekly_digest_day,
            hour=settings.weekly_digest_hour,
            minute=0,
            id="weekly_digest",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    _scheduler.start()
    logger.info(
        "Scheduler started (scan=%s, weekly_digest=%s)",
        f"every {settings.scan_interval_minutes} min" if scan_enabled else "off",
        "on" if digest_enabled else "off",
    )
    return _scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
