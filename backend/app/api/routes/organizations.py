"""Teams / organizations API.

Premium+ users create an organization and invite members who get *read-only*
visibility into the owner's workspace (currently: the owner's dashboard summary).
This is additive — it never mutates the existing user-scoped tables. All routes
require authentication; creation additionally requires a premium/enterprise plan.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ...core.database import get_db
from ...core.plans import require_plan
from ...models.alert import Alert
from ...models.analysis import Analysis
from ...models.cleanup import CleanupAction
from ...models.mention import Mention
from ...models.organization import Organization, OrganizationMember
from ...models.scan import Scan
from ...models.user import User
from ...schemas.dashboard import DashboardSummary
from ...schemas.organization import MemberIn, MemberOut, OrgIn, OrgOut
from ...services.organization import (
    create_org,
    invite_member,
    is_member,
    list_orgs_for,
    resolve_owner,
)
from ...services.scoring import reputation_band
from ..deps import get_current_user

router = APIRouter(prefix="/orgs", tags=["orgs"])


def _get_org_or_404(db: Session, org_id: str) -> Organization:
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


def _require_owner(org: Organization, user: User) -> None:
    if org.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the organization owner may perform this action",
        )


def _build_dashboard_summary(db: Session, owner: User) -> DashboardSummary:
    """Compute the dashboard summary for ``owner``.

    Mirrors the shape/logic of ``routes/dashboard.py`` but scoped to an arbitrary
    workspace owner so an org member can view it read-only.
    """
    uid = owner.id

    total_mentions = db.scalar(
        select(func.count()).select_from(Mention).where(Mention.user_id == uid)
    ) or 0

    sentiment_rows = db.execute(
        select(Analysis.sentiment, func.count())
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == uid)
        .group_by(Analysis.sentiment)
    ).all()
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for sentiment, count in sentiment_rows:
        sentiment_counts[sentiment] = count

    high_risk_count = db.scalar(
        select(func.count())
        .select_from(Analysis)
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == uid, Analysis.risk_level >= 4)
    ) or 0

    unread_alerts = db.scalar(
        select(func.count())
        .select_from(Alert)
        .where(Alert.user_id == uid, Alert.is_read == False)  # noqa: E712
    ) or 0

    active_cleanup = db.scalar(
        select(func.count())
        .select_from(CleanupAction)
        .where(CleanupAction.user_id == uid, CleanupAction.status.in_(("suggested", "in_progress")))
    ) or 0

    last_scan = db.scalar(
        select(Scan)
        .where(Scan.user_id == uid, Scan.status == "completed")
        .order_by(Scan.finished_at.desc())
        .limit(1)
    )

    top_alerts = db.scalars(
        select(Alert)
        .where(Alert.user_id == uid)
        .order_by(Alert.is_read.asc(), Alert.created_at.desc())
        .limit(5)
    ).all()

    recent_high_risk = db.scalars(
        select(Mention)
        .options(selectinload(Mention.analysis))
        .join(Analysis, Analysis.mention_id == Mention.id)
        .where(Mention.user_id == uid, Analysis.risk_level >= 3)
        .order_by(Analysis.risk_level.desc(), Mention.discovered_at.desc())
        .limit(5)
    ).all()

    return DashboardSummary(
        reputation_score=owner.reputation_score,
        band=reputation_band(owner.reputation_score),
        total_mentions=total_mentions,
        sentiment_counts=sentiment_counts,
        high_risk_count=high_risk_count,
        unread_alerts=unread_alerts,
        active_cleanup_actions=active_cleanup,
        last_scan_at=last_scan.finished_at.isoformat() if last_scan and last_scan.finished_at else None,
        top_alerts=top_alerts,
        recent_high_risk=recent_high_risk,
    )


@router.get("", response_model=list[OrgOut])
def list_my_orgs(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List orgs the user owns or is an active member of, with their role."""
    return [
        OrgOut(
            id=org.id,
            name=org.name,
            owner_id=org.owner_id,
            created_at=org.created_at,
            role=role,
        )
        for org, role in list_orgs_for(db, current_user)
    ]


@router.post("", response_model=OrgOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrgIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_plan("pro", "premium", "enterprise")),
):
    """Create an organization (paid tiers — Teams is surfaced as a Pro feature)."""
    org = create_org(db, current_user, payload.name)
    return OrgOut(
        id=org.id,
        name=org.name,
        owner_id=org.owner_id,
        created_at=org.created_at,
        role="owner",
    )


@router.get("/{org_id}/members", response_model=list[MemberOut])
def list_members(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List an org's members. Allowed for the owner or any active member."""
    org = _get_org_or_404(db, org_id)
    if is_member(db, org, current_user) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization",
        )
    return db.scalars(
        select(OrganizationMember).where(OrganizationMember.org_id == org.id)
    ).all()


@router.post("/{org_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def invite_organization_member(
    org_id: str,
    payload: MemberIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a member by email (owner only)."""
    org = _get_org_or_404(db, org_id)
    _require_owner(org, current_user)
    return invite_member(db, org, str(payload.email))


@router.delete("/{org_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_organization_member(
    org_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a member from an org (owner only)."""
    org = _get_org_or_404(db, org_id)
    _require_owner(org, current_user)
    member = db.get(OrganizationMember, member_id)
    if member is None or member.org_id != org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    db.delete(member)
    db.commit()


@router.get("/{org_id}/dashboard", response_model=DashboardSummary)
def org_dashboard(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the OWNER's dashboard summary, read-only.

    Allowed for the org owner or an active member; anyone else gets 403.
    """
    org = _get_org_or_404(db, org_id)
    if is_member(db, org, current_user) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization",
        )
    owner = resolve_owner(db, org)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization owner not found")
    return _build_dashboard_summary(db, owner)
