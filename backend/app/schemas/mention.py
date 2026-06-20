from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AnalysisOut(BaseModel):
    sentiment: str
    sentiment_score: float
    risk_level: int
    risk_category: str
    context: str | None = None
    summary: str | None = None
    recommendation: str | None = None
    analyzer: str
    confidence: float

    model_config = {"from_attributes": True}


class MentionOut(BaseModel):
    id: str
    source: str
    url: str | None = None
    author: str | None = None
    title: str | None = None
    content: str
    status: str
    published_at: datetime | None = None
    discovered_at: datetime
    analysis: AnalysisOut | None = None

    model_config = {"from_attributes": True}


class MentionStatusUpdate(BaseModel):
    status: str  # active | archived | removal_requested | removed


class FixSuggestionOut(BaseModel):
    """An AI-suggested fix for a flagged mention.

    ``kind`` is ``rewrite`` for the user's own connected-account posts (a safer
    rewritten version of the post) or ``response`` for third-party mentions (a
    polite correction / removal-request outline).
    """

    kind: str  # rewrite | response
    suggestion: str
    rationale: str
