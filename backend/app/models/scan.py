from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Scan(Base):
    """A single scan run across all configured connectors for one user."""

    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|running|completed|failed
    trigger: Mapped[str] = mapped_column(String(20), default="manual")  # manual|scheduled

    connectors_used: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mentions_found: Mapped[int] = mapped_column(Integer, default=0)
    new_mentions: Mapped[int] = mapped_column(Integer, default=0)

    score_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_after: Mapped[float | None] = mapped_column(Float, nullable=True)

    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="scans")
