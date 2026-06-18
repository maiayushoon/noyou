"""Organization (teams) service helpers.

Pure persistence/query helpers for the teams feature: create orgs, list the orgs a
user can see (owns or is an active member of), invite members by email, and resolve
membership. All functions are additive — they touch only the new ``organizations`` /
``organization_members`` tables and read-only-reference ``users``.
"""
from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models.organization import Organization, OrganizationMember
from ..models.user import User


def create_org(db: Session, user: User, name: str) -> Organization:
    """Create an organization owned by ``user`` and persist it."""
    org = Organization(name=name, owner_id=user.id)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def list_orgs_for(db: Session, user: User) -> list[tuple[Organization, str]]:
    """Return ``(org, role)`` pairs for every org the user can see.

    Includes orgs the user owns (role ``"owner"``) and orgs where they are an
    *active* member (their member ``role``). Owned orgs take precedence if a user
    were ever both. Ordered newest-first by creation time.
    """
    pairs: dict[str, tuple[Organization, str]] = {}

    owned = db.scalars(
        select(Organization).where(Organization.owner_id == user.id)
    ).all()
    for org in owned:
        pairs[org.id] = (org, "owner")

    member_rows = db.execute(
        select(Organization, OrganizationMember.role)
        .join(OrganizationMember, OrganizationMember.org_id == Organization.id)
        .where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.status == "active",
        )
    ).all()
    for org, role in member_rows:
        # Don't let a membership row shadow ownership.
        pairs.setdefault(org.id, (org, role))

    return sorted(pairs.values(), key=lambda p: p[0].created_at, reverse=True)


def invite_member(db: Session, org: Organization, email: str) -> OrganizationMember:
    """Invite ``email`` to ``org`` (idempotent per email).

    If a registered :class:`User` already has this email, link ``user_id`` and mark
    the membership ``active`` immediately; otherwise it stays ``invited`` until a
    matching user appears. Re-inviting an existing member returns the existing row
    (upgrading it to active if the user now exists).
    """
    normalized = email.strip().lower()

    member = db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.org_id == org.id,
            OrganizationMember.email == normalized,
        )
    )
    if member is None:
        member = OrganizationMember(org_id=org.id, email=normalized)
        db.add(member)

    # Link a registered user with this email so they get immediate read access.
    existing_user = db.scalar(select(User).where(User.email == normalized))
    if existing_user is not None:
        member.user_id = existing_user.id
        member.status = "active"

    db.commit()
    db.refresh(member)
    return member


def is_member(db: Session, org: Organization, user: User) -> str | None:
    """Return the user's role in ``org``, or ``None`` if they have no access.

    The owner gets ``"owner"``; an active member gets their member role. Invited
    (not-yet-active) members are *not* considered members for access purposes.
    """
    if org.owner_id == user.id:
        return "owner"
    member = db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.org_id == org.id,
            OrganizationMember.user_id == user.id,
            OrganizationMember.status == "active",
        )
    )
    return member.role if member else None


def resolve_owner(db: Session, org: Organization) -> User | None:
    """Return the owning :class:`User` whose workspace members can view."""
    return db.get(User, org.owner_id)
