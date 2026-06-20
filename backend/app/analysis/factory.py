"""Selects the active analyzer from config, with safe fallback."""
from __future__ import annotations

from functools import lru_cache

from ..core.config import settings
from .base import BaseAnalyzer
from .rule_based import RuleBasedAnalyzer


@lru_cache
def get_analyzer() -> BaseAnalyzer:
    choice = (settings.analyzer or "rule_based").lower()

    if choice == "trained":
        # Our own trained model. Safe even if untrained — it falls back to rules.
        from .trained import TrainedModelAnalyzer

        return TrainedModelAnalyzer()

    if choice == "llm":
        key_present = any(
            [settings.openai_api_key, settings.anthropic_api_key, settings.huggingface_api_key]
        )
        if key_present:
            from .llm import LLMAnalyzer  # imported lazily so httpx isn't required offline

            return LLMAnalyzer()
        # No key configured — fall back rather than fail.
        return RuleBasedAnalyzer()

    return RuleBasedAnalyzer()
