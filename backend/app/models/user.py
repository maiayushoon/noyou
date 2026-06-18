from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    # Email verification for public signup (enforced only when REQUIRE_EMAIL_VERIFICATION=true).
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Subscription tier from the monetization plan: free | pro | premium | enterprise
    plan: Mapped[str] = mapped_column(String(20), default="free")

    # Latest aggregated reputation score (0-100), cached for fast dashboard loads.
    reputation_score: Mapped[float] = mapped_column(Float, default=100.0)

    # Tokens issued before this moment are rejected — bumped on password reset so a
    # reset invalidates any still-valid stolen access tokens.
    password_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Stripe billing linkage (set once the user subscribes).
    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subscription_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    mentions: Mapped[list["Mention"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    scans: Mapped[list["Scan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
