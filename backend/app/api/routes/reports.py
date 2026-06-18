from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.user import User
from ...services import reports as report_svc
from ..deps import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def full_report(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Aggregated analytics: sentiment, risk categories, sources, and trends."""
    return report_svc.full_report(db, current_user)
