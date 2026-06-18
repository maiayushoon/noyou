from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Analysis(Base):
    """AI analysis attached to a mention: sentiment, risk, category and reasoning."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    mention_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("mentions.id"), unique=True, index=True
    )

    sentiment: Mapped[str] = mapped_column(String(10))          # positive | neutral | negative
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)  # -1.0 .. +1.0

    risk_level: Mapped[int] = mapped_column(Integer, default=0)         # 0 (none) .. 5 (severe)
    risk_category: Mapped[str] = mapped_column(String(20), default="none")
    # one of: none | career | personal | privacy | financial | legal

    context: Mapped[str | None] = mapped_column(String(200), nullable=True)  # short context label
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)         # AI reasoning / why
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)  # suggested action

    analyzer: Mapped[str] = mapped_column(String(30), default="rule_based")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    mention: Mapped["Mention"] = relationship(back_populates="analysis")
