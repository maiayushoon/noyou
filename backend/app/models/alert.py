from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    """A notification raised about a high-risk mention or score change."""

    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    mention_id: Mapped[str | None] = mapped_column(
        GUID, ForeignKey("mentions.id"), nullable=True, index=True
    )

    severity: Mapped[str] = mapped_column(String(10), default="medium")  # low | medium | high | critical
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str] = mapped_column(Text, default="")

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)  # was a notification dispatched

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="alerts")
    mention: Mapped["Mention | None"] = relationship(back_populates="alerts")
