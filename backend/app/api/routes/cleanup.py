from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.cleanup import CleanupAction
from ...models.user import User
from ...schemas.cleanup import CleanupActionOut, CleanupStatusUpdate
from ..deps import get_current_user

router = APIRouter(prefix="/cleanup", tags=["cleanup"])

_VALID = {"suggested", "in_progress", "completed", "dismissed"}


@router.get("", response_model=list[CleanupActionOut])
def list_actions(
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(CleanupAction).where(CleanupAction.user_id == current_user.id)
    if status:
        stmt = stmt.where(CleanupAction.status == status)
    stmt = stmt.order_by(CleanupAction.created_at.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.patch("/{action_id}", response_model=CleanupActionOut)
def update_action(
    action_id: str,
    payload: CleanupStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in _VALID:
        raise HTTPException(status_code=422, detail=f"status must be one of {_VALID}")
    action = db.get(CleanupAction, action_id)
    if not action or action.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cleanup action not found")
    action.status = payload.status
    if payload.status == "completed":
        action.completed_at = datetime.now(timezone.utc)
    db.add(action)
    db.commit()
    db.refresh(action)
    return action
