"""Schemas for the AI Visibility (GEO/AEO) feature.

AI Visibility answers "how discoverable and representable is my brand to AI answer
engines (ChatGPT, Perplexity, Google AI Overviews, Gemini)?". We derive a 0-100
GEO score from the user's own scanned mentions plus heuristics, surface the
individual signals that fed the score, and return concrete recommendations the user
can act on to be surfaced and cited more often by AI engines.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class AiVisibilitySignal(BaseModel):
    """One evaluated GEO/AI-visibility signal and whether the brand satisfies it."""

    name: str = Field(description="Stable signal key, e.g. 'social_presence'.")
    present: bool = Field(description="Whether the brand currently satisfies the signal.")
    weight: int = Field(description="Relative contribution of this signal to the score.")
    detail: str = Field(description="Human-readable explanation of the signal's status.")


class AiVisibilityResponse(BaseModel):
    """The full AI-visibility assessment for a brand.

    ``band`` buckets ``ai_visibility_score`` into one of:
      * ``low``       — barely discoverable by AI engines
      * ``medium``    — some presence, notable gaps
      * ``high``      — well represented, minor gaps
      * ``excellent`` — strongly surfaced and citable
    """

    brand: str
    ai_visibility_score: float = Field(ge=0.0, le=100.0)
    band: str  # low | medium | high | excellent
    signals: list[AiVisibilitySignal] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    summary: str
    llm_used: bool = False
