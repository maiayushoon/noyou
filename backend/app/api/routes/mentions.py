from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...core.database import get_db
from ...models.analysis import Analysis
from ...models.mention import Mention
from ...models.user import User
from ...schemas.mention import MentionOut, MentionStatusUpdate
from ...services.scanning import recompute_user_score
from ..deps import get_current_user

router = APIRouter(prefix="/mentions", tags=["mentions"])

_VALID_STATUSES = {"active", "archived", "removal_requested", "removed"}


@router.get("", response_model=list[MentionOut])
def list_mentions(
    sentiment: str | None = Query(default=None),
    min_risk: int = Query(default=0, ge=0, le=5),
    source: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Mention)
        .options(selectinload(Mention.analysis))
        .join(Analysis, Analysis.mention_id == Mention.id, isouter=True)
        .where(Mention.user_id == current_user.id)
    )
    if sentiment:
        stmt = stmt.where(Analysis.sentiment == sentiment)
    if min_risk:
        stmt = stmt.where(Analysis.risk_level >= min_risk)
    if source:
        stmt = stmt.where(Mention.source == source)
    if status:
        stmt = stmt.where(Mention.status == status)
    stmt = stmt.order_by(Analysis.risk_level.desc(), Mention.discovered_at.desc())
    stmt = stmt.offset(offset).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{mention_id}", response_model=MentionOut)
def get_mention(
    mention_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mention = db.get(Mention, mention_id)
    if not mention or mention.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Mention not found")
    return mention


@router.patch("/{mention_id}/status", response_model=MentionOut)
def update_status(
    mention_id: str,
    payload: MentionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in _VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {_VALID_STATUSES}")
    mention = db.get(Mention, mention_id)
    if not mention or mention.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Mention not found")
    mention.status = payload.status
    db.add(mention)
    db.commit()
    # Cleaning up content changes the score, so recompute.
    recompute_user_score(db, current_user)
    db.refresh(mention)
    return mention
