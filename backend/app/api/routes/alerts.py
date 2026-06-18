from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.alert import Alert
from ...models.user import User
from ...schemas.alert import AlertOut
from ..deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Alert).where(Alert.user_id == current_user.id)
    if unread_only:
        stmt = stmt.where(Alert.is_read == False)  # noqa: E712
    stmt = stmt.order_by(Alert.created_at.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.post("/{alert_id}/read", response_model=AlertOut)
def mark_read(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.get(Alert, alert_id)
    if not alert or alert.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/read-all", status_code=204)
def mark_all_read(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    alerts = db.scalars(
        select(Alert).where(Alert.user_id == current_user.id, Alert.is_read == False)  # noqa: E712
    ).all()
    for alert in alerts:
        alert.is_read = True
    db.commit()
