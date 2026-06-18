from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CleanupAction(Base):
    """A recommended or executed cleanup step for a risky mention.

    For the MVP these are *suggestions* the user performs manually (action_type
    describes what to do). The same model supports automated execution later — the
    ``status`` field tracks the lifecycle either way.
    """

    __tablename__ = "cleanup_actions"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    mention_id: Mapped[str] = mapped_column(GUID, ForeignKey("mentions.id"), index=True)

    action_type: Mapped[str] = mapped_column(String(30))  # delete_post | request_removal | archive | dispute | monitor
    title: Mapped[str] = mapped_column(String(300))
    instructions: Mapped[str] = mapped_column(Text, default="")

    # suggested | in_progress | completed | dismissed
    status: Mapped[str] = mapped_column(String(20), default="suggested")
    automated: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    mention: Mapped["Mention"] = relationship(back_populates="cleanup_actions")
