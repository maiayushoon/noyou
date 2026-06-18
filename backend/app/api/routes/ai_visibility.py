"""AI Visibility (GEO/AEO) route.

Tells a user how discoverable and representable their brand is to AI answer engines
(ChatGPT, Perplexity, Google AI Overviews, Gemini), returning a 0-100 GEO score, the
signals behind it, and concrete recommendations. Gated to Pro and above via the
``predictive`` feature flag (this is part of the predictive/AI insight suite).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.plans import require_feature
from ...models.user import User
from ...schemas.ai_visibility import AiVisibilityResponse
from ...services import ai_visibility as ai_visibility_svc

router = APIRouter(prefix="/ai-visibility", tags=["ai-visibility"])

# AI Visibility is part of the paid predictive/AI insight suite (Pro and above).
# require_feature both authenticates the user and enforces the plan gate.
require_predictive = require_feature("predictive")


@router.get("", response_model=AiVisibilityResponse)
def ai_visibility(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_predictive),
) -> AiVisibilityResponse:
    """Assess how discoverable the current user's primary brand is to AI answer engines."""
    return ai_visibility_svc.assess(db, current_user)
