from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    """A monitored identity on a platform that the user has linked.

    For demo/MVP we store the public handle and the search terms to scan for. OAuth
    tokens (for authenticated APIs) go in ``access_token`` / ``refresh_token`` later.
    """

    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)

    platform: Mapped[str] = mapped_column(String(40))   # google, twitter, linkedin, ...
    handle: Mapped[str] = mapped_column(String(200))    # @name / profile id / search term
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    profile_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # OAuth credentials for authenticated platform APIs (optional, future use).
    access_token: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="accounts")
