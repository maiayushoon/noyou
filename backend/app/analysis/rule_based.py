"""Offline lexicon analyzer — the default brain.

No network, no keys, deterministic and explainable. It computes a sentiment score
from positive/negative word weights (with negation + intensifier handling), detects
the dominant risk category and level from keyword hits, and writes a short
human-readable rationale and recommendation. Good enough for a real demo and a
sane baseline the LLM analyzer can be A/B-tested against.
"""
from __future__ import annotations

import re

from .base import AnalysisInput, AnalysisResult, BaseAnalyzer
from .lexicon import (
    CONTEXT_SOFTENERS,
    INTENSIFIERS,
    NEGATIVE_WORDS,
    NEGATORS,
    POSITIVE_WORDS,
    RISK_KEYWORDS,
)

_WORD_RE = re.compile(r"[a-z']+")


class RuleBasedAnalyzer(BaseAnalyzer):
    name = "rule_based"

    def analyze(self, item: AnalysisInput) -> AnalysisResult:
        text = f"{item.title or ''} {item.content or ''}".lower()
        tokens = _WORD_RE.findall(text)

        sentiment_score = self._score_sentiment(tokens)
        risk_level, risk_category, hits = self._score_risk(text)

        softened = any(s in text for s in CONTEXT_SOFTENERS)
        if softened and sentiment_score < 0:
            sentiment_score += 0.25  # likely the subject is the protagonist, not the villain
            risk_level = max(0, risk_level - 1)

        sentiment = (
            "positive" if sentiment_score > 0.15
            else "negative" if sentiment_score < -0.15
            else "neutral"
        )

        # A purely positive/neutral mention carries no risk regardless of keyword noise.
        if sentiment == "positive" and risk_level <= 2:
            risk_level, risk_category = 0, "none"

        context = self._context_label(sentiment, risk_category, risk_level)
        summary = self._summary(sentiment, sentiment_score, risk_category, risk_level, hits)
        recommendation = self._recommendation(sentiment, risk_category, risk_level)
        confidence = self._confidence(tokens, hits, sentiment_score)

        return AnalysisResult(
            sentiment=sentiment,
            sentiment_score=round(sentiment_score, 3),
            risk_level=risk_level,
            risk_category=risk_category,
            context=context,
            summary=summary,
            recommendation=recommendation,
            analyzer=self.name,
            confidence=confidence,
            tags=sorted(hits.keys()),
        ).validate()

    # --- internals -----------------------------------------------------------
    def _score_sentiment(self, tokens: list[str]) -> float:
        total = 0.0
        count = 0
        for i, tok in enumerate(tokens):
            weight = POSITIVE_WORDS.get(tok, 0.0) - NEGATIVE_WORDS.get(tok, 0.0)
            if weight == 0.0:
                continue
            # look back up to 2 tokens for negators / intensifiers
            window = tokens[max(0, i - 2):i]
            if any(w in NEGATORS for w in window):
                weight = -weight
            for w in window:
                if w in INTENSIFIERS:
                    weight *= INTENSIFIERS[w]
            total += weight
            count += 1
        if count == 0:
            return 0.0
        # Normalise by sqrt(count) so a few strong words still register but long
        # neutral text isn't over-diluted.
        return max(-1.0, min(1.0, total / (count ** 0.5)))

    def _score_risk(self, text: str) -> tuple[int, str, dict[str, int]]:
        hits: dict[str, int] = {}
        category_scores: dict[str, int] = {}
        for keyword, (category, base) in RISK_KEYWORDS.items():
            if keyword in text:
                hits[keyword] = base
                category_scores[category] = max(category_scores.get(category, 0), base)
        if not category_scores:
            return 0, "none", hits
        category = max(category_scores, key=category_scores.get)
        # Multiple distinct risk hits compound the level slightly.
        level = category_scores[category]
        if len(hits) >= 3:
            level = min(5, level + 1)
        return level, category, hits

    def _context_label(self, sentiment: str, category: str, level: int) -> str:
        if level >= 4:
            return f"high-risk {category} content"
        if level >= 1:
            return f"{category} concern"
        if sentiment == "positive":
            return "positive coverage"
        if sentiment == "negative":
            return "negative sentiment"
        return "neutral mention"

    def _summary(self, sentiment, score, category, level, hits) -> str:
        parts = [f"Sentiment is {sentiment} (score {score:+.2f})."]
        if level > 0:
            kw = ", ".join(sorted(hits)[:4])
            parts.append(f"Detected {category} risk at level {level}/5 from signals: {kw}.")
        else:
            parts.append("No material reputational risk detected.")
        return " ".join(parts)

    def _recommendation(self, sentiment: str, category: str, level: int) -> str:
        if level >= 4:
            return (
                f"Act now: this {category} content can materially damage you. Request "
                "removal from the source/platform, document it, and consider legal or PR support."
            )
        if level >= 2:
            return (
                f"Monitor closely and consider requesting correction or removal of this "
                f"{category} content. Prepare a response in case it spreads."
            )
        if sentiment == "negative":
            return "Low risk, but keep an eye on it. Engage politely if a response is warranted."
        if sentiment == "positive":
            return "Positive for your reputation — amplify or reference it where useful."
        return "No action needed."

    def _confidence(self, tokens, hits, score) -> float:
        # More signal words and stronger scores => higher confidence.
        signal = abs(score) + 0.15 * len(hits)
        base = 0.45 + min(0.45, signal)
        if len(tokens) < 4:
            base -= 0.15
        return round(max(0.2, min(0.95, base)), 2)
