from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Mention(Base):
    """A piece of content found about the user on the web or a platform."""

    __tablename__ = "mentions"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    scan_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("scans.id"), nullable=True, index=True)

    source: Mapped[str] = mapped_column(String(40), index=True)   # google, twitter, reddit...
    external_id: Mapped[str] = mapped_column(String(300), index=True)  # dedupe key from source
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")

    # Lifecycle so we can drive cleanup workflows: active | archived | removal_requested | removed
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="mentions")
    analysis: Mapped["Analysis | None"] = relationship(
        back_populates="mention", uselist=False, cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="mention", cascade="all, delete-orphan"
    )
    cleanup_actions: Mapped[list["CleanupAction"]] = relationship(
        back_populates="mention", cascade="all, delete-orphan"
    )
