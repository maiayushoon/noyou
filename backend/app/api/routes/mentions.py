from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...analysis.base import AnalysisResult
from ...analysis.suggest import build_suggestion
from ...core.database import get_db
from ...core.plans import require_plan
from ...models.analysis import Analysis
from ...models.mention import Mention
from ...models.user import User
from ...schemas.mention import FixSuggestionOut, MentionOut, MentionStatusUpdate
from ...services.scanning import recompute_user_score
from ..deps import get_current_user

router = APIRouter(prefix="/mentions", tags=["mentions"])

_VALID_STATUSES = {"active", "archived", "removal_requested", "removed"}

# AI-suggested fixes are a paid feature (Pro and above).
require_suggest = require_plan("pro", "premium", "enterprise")


def _analysis_result(analysis: Analysis | None) -> AnalysisResult:
    """Adapt a stored ``Analysis`` row into the analyzer's ``AnalysisResult``.

    When a mention has no analysis yet we still return a valid, neutral result so
    the suggestion helper has a stable shape to reason about.
    """
    if analysis is None:
        return AnalysisResult().validate()
    return AnalysisResult(
        sentiment=analysis.sentiment,
        sentiment_score=analysis.sentiment_score,
        risk_level=analysis.risk_level,
        risk_category=analysis.risk_category,
        context=analysis.context,
        summary=analysis.summary,
        recommendation=analysis.recommendation,
        analyzer=analysis.analyzer,
        confidence=analysis.confidence,
    ).validate()


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


@router.post("/{mention_id}/suggest", response_model=FixSuggestionOut)
def suggest_fix(
    mention_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_suggest),
) -> FixSuggestionOut:
    """Return a concrete AI-suggested fix for a flagged mention (Pro and above).

    For the user's OWN connected-account posts (source ends with ``_owned``) the
    suggestion is a safer rewritten version of the post (``kind="rewrite"``); for
    third-party mentions it's a polite correction / removal-request outline
    (``kind="response"``).

    The suggestion is produced by the active analyzer's LLM path when configured,
    and otherwise by a deterministic rule-based template. The LLM path degrades to
    the rule-based suggestion on any error, so this endpoint never 500s on it.
    """
    mention = db.get(Mention, mention_id)
    if not mention or mention.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Mention not found")

    result = build_suggestion(
        content=mention.content or "",
        source=mention.source,
        analysis=_analysis_result(mention.analysis),
    )
    return FixSuggestionOut(
        kind=result.kind,
        suggestion=result.suggestion,
        rationale=result.rationale,
    )
