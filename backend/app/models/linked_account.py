from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LinkedAccount(Base):
    """An OAuth-authorized connection to the user's OWN account on a platform.

    DISTINCT from :class:`~app.models.account.Account` (monitored identities /
    search seeds). Tokens are stored ENCRYPTED (Fernet); plaintext never touches
    the DB or logs. Owned content read with these tokens flows through the normal
    scan pipeline as ``RawMention`` records, sourced as ``{provider}_owned``.
    """

    __tablename__ = "linked_accounts"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "provider", "external_id", name="uq_linked_user_provider_extid"
        ),
    )

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    # mastodon|youtube|reddit|threads|instagram|twitter|tiktok
    provider: Mapped[str] = mapped_column(String(40), index=True)
    # connected|expired|revoked|error
    status: Mapped[str] = mapped_column(String(20), default="connected")
    # provider user/channel id (NOT secret)
    external_id: Mapped[str] = mapped_column(String(190))
    external_handle: Mapped[str | None] = mapped_column(String(200), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Mastodon per-instance base; else NULL.
    instance_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # Fernet ciphertext (never plaintext).
    access_token_enc: Mapped[str] = mapped_column(Text)
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # space-delimited granted scopes
    scopes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    user: Mapped["User"] = relationship(back_populates="linked_accounts")
