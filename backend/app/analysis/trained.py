"""Analyzer backed by NoYou's own trained sentiment model.

A hybrid brain: the **learned model** decides sentiment (the part that benefits from
training data), while the proven **rule-based** engine supplies risk level, category,
context and recommendations. If no model has been trained yet, it transparently
behaves exactly like the rule-based analyzer — so ``ANALYZER=trained`` is always safe.

Train/refresh the model with ``python -m app.ml.train``.
"""
from __future__ import annotations

import json

from .base import AnalysisInput, AnalysisResult, BaseAnalyzer
from .rule_based import RuleBasedAnalyzer


class TrainedModelAnalyzer(BaseAnalyzer):
    name = "trained"

    def __init__(self) -> None:
        self._fallback = RuleBasedAnalyzer()
        self._model = None
        self._meta: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            import joblib

            from ..ml.store import meta_file, model_file

            path = model_file()
            if path.exists():
                self._model = joblib.load(path)
                mp = meta_file()
                if mp.exists():
                    self._meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            self._model = None  # any load problem → behave like rule-based

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def analyze(self, item: AnalysisInput) -> AnalysisResult:
        # Start from the rule-based result for rich risk/recommendation fields.
        result = self._fallback.analyze(item)
        if self._model is None:
            return result  # no trained model yet → pure rule-based

        text = f"{item.title or ''} {item.content or ''}".strip()
        if not text:
            return result
        try:
            classes = list(self._model.classes_)
            proba = self._model.predict_proba([text])[0]
            scores = dict(zip(classes, (float(p) for p in proba)))
            sentiment = max(scores, key=scores.get)
            confidence = scores[sentiment]
            # Signed score in [-1, 1]: positive mass minus negative mass.
            sentiment_score = scores.get("positive", 0.0) - scores.get("negative", 0.0)
        except Exception:
            return result  # prediction failed → keep rule-based result

        result.sentiment = sentiment
        result.sentiment_score = sentiment_score
        result.confidence = confidence
        result.analyzer = f"trained:v{self._meta.get('version', '?')}"
        return result.validate()
