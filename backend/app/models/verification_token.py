from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class VerificationToken(Base):
    """A single-use, time-limited token for email verification or password reset.

    One row is created per request (sign-up confirmation, "resend verification",
    or "forgot password"). The opaque ``token`` value is the only thing emailed to
    the user; it is looked up here to resolve the owning user, then marked ``used``
    so it cannot be replayed.
    """

    __tablename__ = "verification_tokens"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("users.id"), index=True, nullable=False
    )

    # Opaque, URL-safe secret handed to the user; indexed + unique for fast,
    # collision-free lookups.
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # "verify" (email verification) | "reset" (password reset).
    purpose: Mapped[str] = mapped_column(String(10), nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship()
