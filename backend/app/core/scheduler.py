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


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if settings.scan_interval_minutes <= 0:
        logger.info("Scheduler disabled (SCAN_INTERVAL_MINUTES=0)")
        return None
    if _scheduler and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _scan_all_users,
        "interval",
        minutes=settings.scan_interval_minutes,
        id="periodic_scan",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    _scheduler.start()
    logger.info("Scheduler started: scanning every %s min", settings.scan_interval_minutes)
    return _scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
