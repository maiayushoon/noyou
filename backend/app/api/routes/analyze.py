"""Predictive pre-post analysis — "will this post hurt my reputation?".

Unlike the rest of the API, these endpoints never touch the database. The user
submits a *draft* (something they're thinking about posting), we run it through
the same analyzer that scores discovered mentions, and we return a publish
verdict so the UI can warn them before they hit send.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ...analysis import get_analyzer
from ...analysis.base import AnalysisInput, AnalysisResult
from ...core.plans import require_feature
from ...models.user import User
from ...schemas.analyze import DraftAnalyzeRequest, DraftAnalyzeResponse

router = APIRouter(prefix="/analyze", tags=["analyze"])

# Predictive pre-post analysis is a paid feature (Pro and above). require_feature
# both authenticates the user and enforces the plan gate, returning the User.
require_predictive = require_feature("predictive")

# Publish-verdict vocabulary, kept here so callers and the UI agree on the labels.
SAFE_TO_POST = "safe_to_post"
REVIEW_SUGGESTED = "review_suggested"
DO_NOT_POST = "do_not_post"


def _publish_recommendation(result: AnalysisResult) -> str:
    """Derive a publish verdict from the analyzer's risk level and sentiment.

    The thresholds intentionally err toward caution: a negative tone alone is
    enough to suggest a second read, and a moderately-negative high-risk draft is
    flagged as do-not-post even when neither signal is extreme on its own.
    """
    negative = result.sentiment == "negative"
    risk = result.risk_level

    if risk >= 4 or (negative and risk >= 3):
        return DO_NOT_POST
    if risk >= 2 or negative:
        return REVIEW_SUGGESTED
    return SAFE_TO_POST


def _to_response(result: AnalysisResult) -> DraftAnalyzeResponse:
    """Map an ``AnalysisResult`` onto the API response, adding the verdict."""
    return DraftAnalyzeResponse(
        sentiment=result.sentiment,
        sentiment_score=result.sentiment_score,
        risk_level=result.risk_level,
        risk_category=result.risk_category,
        context=result.context,
        summary=result.summary,
        recommendation=result.recommendation,
        analyzer=result.analyzer,
        confidence=result.confidence,
        publish_recommendation=_publish_recommendation(result),
        flagged_terms=list(result.tags),
    )


@router.post("", response_model=DraftAnalyzeResponse)
def analyze_draft(
    req: DraftAnalyzeRequest,
    current_user: User = Depends(require_predictive),
) -> DraftAnalyzeResponse:
    """Score a draft post and return a publish verdict. Persists nothing."""
    # Use the user's own name/email as the monitored subject so the analyzer can
    # reason about first-person reputational risk.
    subject_name = current_user.full_name or current_user.email
    result = get_analyzer().analyze(
        AnalysisInput(content=req.text, subject_name=subject_name)
    ).validate()
    return _to_response(result)


@router.get("/examples", response_model=list[DraftAnalyzeResponse])
def analyze_examples(
    current_user: User = Depends(require_predictive),
) -> list[DraftAnalyzeResponse]:
    """A few sample drafts scored live, so the UI can show what verdicts look like."""
    subject_name = current_user.full_name or current_user.email
    samples = [
        "Excited to share that our team just shipped a major release. Proud of everyone!",
        "Honestly my manager has no idea what they're doing and the whole company is a joke.",
        "Thinking about the weather this weekend, might go for a hike.",
    ]
    analyzer = get_analyzer()
    return [
        _to_response(analyzer.analyze(AnalysisInput(content=text, subject_name=subject_name)).validate())
        for text in samples
    ]
