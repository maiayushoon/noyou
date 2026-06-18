"""Schemas for the predictive pre-post analysis feature.

A user pastes a draft post *before* publishing it; the analyzer scores it the
same way it scores a discovered mention, and we add a publish verdict on top so
the UI can render a simple green/amber/red signal. Nothing here is persisted.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class DraftAnalyzeRequest(BaseModel):
    """A draft the user is considering posting."""

    text: str = Field(min_length=1, max_length=10000, description="The draft post text to analyze.")
    context: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional surrounding context (audience, platform, intent).",
    )


class DraftAnalyzeResponse(BaseModel):
    """Mirrors ``AnalysisResult`` plus a publish verdict and the flagged terms.

    ``publish_recommendation`` is one of:
      * ``safe_to_post``     — low risk, go ahead
      * ``review_suggested`` — borderline; reread before posting
      * ``do_not_post``      — high risk to the user's reputation
    """

    # --- mirrored AnalysisResult fields ---
    sentiment: str
    sentiment_score: float
    risk_level: int
    risk_category: str
    context: str | None = None
    summary: str | None = None
    recommendation: str | None = None
    analyzer: str
    confidence: float

    # --- predictive additions ---
    publish_recommendation: str  # safe_to_post | review_suggested | do_not_post
    flagged_terms: list[str] = Field(default_factory=list)
