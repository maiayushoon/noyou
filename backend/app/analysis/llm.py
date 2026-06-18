"""LLM-backed analyzer (OpenAI / Anthropic / HuggingFace).

This is a working skeleton: it builds a strict JSON-returning prompt and parses the
response into an ``AnalysisResult``. It only activates when ``ANALYZER=llm`` and the
matching provider key is set; otherwise the factory falls back to the rule-based
analyzer, so the product never breaks because a key is missing.

To keep the dependency footprint light and offline-friendly, the provider calls use
``httpx`` directly rather than each vendor SDK.
"""
from __future__ import annotations

import json

import httpx

from ..core.config import settings
from .base import AnalysisInput, AnalysisResult, BaseAnalyzer
from .rule_based import RuleBasedAnalyzer

SYSTEM_PROMPT = (
    "You are a digital reputation risk analyst. Given a piece of online content about "
    "a person or brand, return ONLY a JSON object with keys: sentiment (positive|neutral|"
    "negative), sentiment_score (-1..1), risk_level (0..5 integer), risk_category "
    "(none|career|personal|privacy|financial|legal), context (short label), summary "
    "(one sentence on why), recommendation (one actionable sentence), confidence (0..1). "
    "No prose outside the JSON."
)


class LLMAnalyzer(BaseAnalyzer):
    name = "llm"

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self._fallback = RuleBasedAnalyzer()

    def analyze(self, item: AnalysisInput) -> AnalysisResult:
        try:
            raw = self._call_provider(self._build_user_prompt(item))
            data = self._parse(raw)
            return AnalysisResult(
                sentiment=data.get("sentiment", "neutral"),
                sentiment_score=float(data.get("sentiment_score", 0.0)),
                risk_level=int(data.get("risk_level", 0)),
                risk_category=data.get("risk_category", "none"),
                context=data.get("context"),
                summary=data.get("summary"),
                recommendation=data.get("recommendation"),
                analyzer=f"llm:{self.provider}",
                confidence=float(data.get("confidence", 0.7)),
            ).validate()
        except Exception:  # network, quota, parse — degrade gracefully, never crash a scan
            result = self._fallback.analyze(item)
            result.analyzer = "rule_based(fallback)"
            return result

    def _build_user_prompt(self, item: AnalysisInput) -> str:
        subject = item.subject_name or "the monitored person/brand"
        return (
            f"Subject: {subject}\nSource: {item.source}\nAuthor: {item.author}\n"
            f"Title: {item.title or ''}\nContent: {item.content}"
        )

    def _parse(self, raw: str) -> dict:
        start, end = raw.find("{"), raw.rfind("}")
        return json.loads(raw[start : end + 1])

    def _call_provider(self, user_prompt: str) -> str:
        if self.provider == "openai":
            return self._openai(user_prompt)
        if self.provider == "anthropic":
            return self._anthropic(user_prompt)
        if self.provider == "huggingface":
            return self._huggingface(user_prompt)
        raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _openai(self, user_prompt: str) -> str:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _anthropic(self, user_prompt: str) -> str:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 400,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    def _huggingface(self, user_prompt: str) -> str:
        # Generic text-generation inference endpoint. Model is configurable later.
        resp = httpx.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct",
            headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
            json={"inputs": f"{SYSTEM_PROMPT}\n\n{user_prompt}", "parameters": {"max_new_tokens": 400}},
            timeout=60,
        )
        resp.raise_for_status()
        out = resp.json()
        return out[0]["generated_text"] if isinstance(out, list) else str(out)
