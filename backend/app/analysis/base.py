"""The AI analysis contract.

Every analyzer — offline lexicon, OpenAI, Anthropic, a fine-tuned HF model —
implements ``BaseAnalyzer.analyze`` and returns an ``AnalysisResult``. Swapping the
brain of the product is a one-line config change (``ANALYZER=...``).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# Canonical vocabularies — kept here so the whole app agrees on the labels.
SENTIMENTS = ("positive", "neutral", "negative")
RISK_CATEGORIES = ("none", "career", "personal", "privacy", "financial", "legal")


@dataclass
class AnalysisResult:
    sentiment: str = "neutral"
    sentiment_score: float = 0.0          # -1.0 (very negative) .. +1.0 (very positive)
    risk_level: int = 0                   # 0 (no risk) .. 5 (severe)
    risk_category: str = "none"
    context: str | None = None            # short human label, e.g. "professional criticism"
    summary: str | None = None            # why the model thinks this
    recommendation: str | None = None     # suggested next step
    analyzer: str = "base"
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)

    def validate(self) -> "AnalysisResult":
        if self.sentiment not in SENTIMENTS:
            self.sentiment = "neutral"
        if self.risk_category not in RISK_CATEGORIES:
            self.risk_category = "none"
        self.risk_level = max(0, min(5, int(self.risk_level)))
        self.sentiment_score = max(-1.0, min(1.0, float(self.sentiment_score)))
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        return self


@dataclass
class AnalysisInput:
    content: str
    title: str | None = None
    source: str | None = None
    author: str | None = None
    subject_name: str | None = None       # the person/brand being monitored


class BaseAnalyzer(ABC):
    name = "base"

    @abstractmethod
    def analyze(self, item: AnalysisInput) -> AnalysisResult:
        """Analyze a single mention and return structured risk/sentiment data."""
        raise NotImplementedError

    def analyze_text(self, content: str, **kwargs) -> AnalysisResult:
        return self.analyze(AnalysisInput(content=content, **kwargs))
