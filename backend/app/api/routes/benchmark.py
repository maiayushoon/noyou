from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.plans import require_feature
from ...models.competitor import Competitor
from ...models.user import User
from ...schemas.benchmark import (
    BenchmarkReport,
    CompetitorIn,
    CompetitorOut,
)
from ...services import benchmark as benchmark_svc
from ..deps import get_current_user

router = APIRouter(prefix="/benchmark", tags=["benchmark"])

# Cap tracked competitors per user so a live benchmark stays bounded.
MAX_COMPETITORS = 5


@router.get("/competitors", response_model=list[CompetitorOut])
def list_competitors(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List the competitors the current user is benchmarking against."""
    return db.scalars(
        select(Competitor)
        .where(Competitor.user_id == current_user.id)
        .order_by(Competitor.created_at)
    ).all()


@router.post("/competitors", response_model=CompetitorOut, status_code=201)
def add_competitor(
    payload: CompetitorIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Track a new competitor name (capped at ``MAX_COMPETITORS`` per user)."""
    current = db.scalar(
        select(func.count()).select_from(Competitor).where(Competitor.user_id == current_user.id)
    ) or 0
    if current >= MAX_COMPETITORS:
        raise HTTPException(
            status_code=402,
            detail=f"You can track up to {MAX_COMPETITORS} competitors.",
        )

    competitor = Competitor(user_id=current_user.id, name=payload.name.strip())
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


@router.delete("/competitors/{competitor_id}", status_code=204)
def remove_competitor(
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop tracking a competitor (ownership-checked)."""
    competitor = db.get(Competitor, competitor_id)
    if not competitor or competitor.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
    db.delete(competitor)
    db.commit()


@router.get("", response_model=BenchmarkReport)
def benchmark_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_feature("benchmarking")),
):
    """Compare the user's reputation against each tracked competitor (premium feature)."""
    return benchmark_svc.run_benchmark(db, current_user)
