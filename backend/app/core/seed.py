"""Seed a demo user (and run an initial scan) so the dashboard has data on first boot."""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .security import hash_password
from ..models.account import Account
from ..models.user import User

logger = logging.getLogger("noyou.seed")


def seed_demo(db: Session) -> None:
    if not settings.seed_demo:
        return

    user = db.scalar(select(User).where(User.email == settings.demo_email))
    if user:
        return  # already seeded

    logger.info("Seeding demo user %s", settings.demo_email)
    user = User(
        email=settings.demo_email,
        full_name="Jordan Demo",
        password_hash=hash_password(settings.demo_password),
        plan="pro",
    )
    db.add(user)
    db.flush()

    db.add_all(
        [
            Account(user_id=user.id, platform="twitter", handle="Jordan Demo", display_name="Jordan Demo"),
            Account(user_id=user.id, platform="google", handle="Jordan Demo"),
        ]
    )
    db.commit()

    # Run an initial scan so the dashboard is populated immediately.
    try:
        from ..services.scanning import run_scan

        run_scan(db, user, trigger="scheduled")
        logger.info("Initial demo scan complete")
    except Exception:
        logger.exception("Initial demo scan failed (app still usable)")
