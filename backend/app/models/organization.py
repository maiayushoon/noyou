from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import GUID, Base, gen_uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    """A team/workspace owned by a single (premium+) user.

    Owners invite members who get *read* access to the owner's workspace via the
    org routes. This is an additive, side-table feature: it never alters the
    existing user-scoped tables or their queries.
    """

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class OrganizationMember(Base):
    """An invited or active member of an :class:`Organization`.

    A member is invited by email. ``user_id`` is linked (and ``status`` flipped to
    ``active``) once a registered :class:`~app.models.user.User` with that email is
    matched — either at invite time or when they accept. Members get read-only
    visibility into the owner's workspace; they never gain write access to it.
    """

    __tablename__ = "organization_members"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(GUID, ForeignKey("organizations.id"), index=True)

    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    # Linked once a registered user with this email accepts/matches the invite.
    user_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("users.id"), nullable=True)

    role: Mapped[str] = mapped_column(String(20), default="member")     # member | admin
    status: Mapped[str] = mapped_column(String(20), default="invited")  # invited | active

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
