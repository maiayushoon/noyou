from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Competitor(Base):
    """A rival name a premium user tracks for benchmarking against their own reputation.

    Competitors are scanned live at report time and never persisted as mentions, so
    this table only stores the user-supplied name (no back-relationship on ``User``;
    callers query by ``user_id`` directly).
    """

    __tablename__ = "competitors"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(200))  # competitor brand / person to benchmark

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
