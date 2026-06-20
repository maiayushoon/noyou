"""AI-suggested fixes for flagged mentions.

For a flagged mention the user can ask for a concrete next step:

  * ``rewrite``  — for the user's OWN connected-account posts (source ends with
    ``_owned``): a calmer, safer version of the post they can edit it to.
  * ``response`` — for third-party mentions they don't control: an outline for a
    polite correction / removal request, or a measured public reply.

The suggestion is produced by the active analyzer's LLM path when ``ANALYZER=llm``
and a provider key is configured; otherwise it falls back to a solid,
deterministic rule-based template built from the stored analysis (sentiment,
risk_category, risk_level and the existing recommendation).

The LLM path NEVER raises out of here — any network/quota/parse problem degrades
silently to the rule-based suggestion, so the endpoint can never 500 on it.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import AnalysisResult
from .factory import get_analyzer

# Sources for content the user OWNS are suffixed with this (kept in sync with
# app/services/alerts.py and the OAuth adapters).
_OWNED_SUFFIX = "_owned"

# Suggestion kinds — the UI agrees on these labels.
KIND_REWRITE = "rewrite"
KIND_RESPONSE = "response"


@dataclass
class FixSuggestion:
    """A concrete suggested fix for a flagged mention."""

    kind: str  # "rewrite" | "response"
    suggestion: str  # the rewritten post, or the response/removal outline
    rationale: str  # one short paragraph on why this helps


def suggestion_kind(source: str | None) -> str:
    """``rewrite`` for the user's own connected-account posts, else ``response``."""
    return KIND_REWRITE if (source or "").endswith(_OWNED_SUFFIX) else KIND_RESPONSE


def _platform_label(source: str | None) -> str:
    """Human platform label from an owned source ("reddit_owned" -> "Reddit")."""
    src = source or ""
    prefix = src[: -len(_OWNED_SUFFIX)] if src.endswith(_OWNED_SUFFIX) else src
    return prefix.replace("_", " ").title() if prefix else "your account"


def build_suggestion(
    *,
    content: str,
    source: str | None,
    analysis: AnalysisResult,
) -> FixSuggestion:
    """Build a fix suggestion, preferring the LLM path and falling back to rules.

    ``analysis`` carries the stored sentiment / risk_category / risk_level /
    recommendation. The kind is decided purely from ``source`` so it is stable
    regardless of which path produced the text.
    """
    kind = suggestion_kind(source)

    llm = _llm_suggestion(content=content, source=source, kind=kind, analysis=analysis)
    if llm is not None:
        return llm

    return _rule_based_suggestion(content=content, source=source, kind=kind, analysis=analysis)


# --- LLM path -------------------------------------------------------------
_SYSTEM_REWRITE = (
    "You help people protect their online reputation. Rewrite the user's OWN social "
    "post into a calmer, factual, professional version that conveys the same point "
    "without inflammatory, risky, or damaging language. Keep it concise. Return ONLY "
    "the rewritten post text, with no preamble, quotes, or commentary."
)
_SYSTEM_RESPONSE = (
    "You help people protect their online reputation. The user has been mentioned in "
    "third-party content they do not control. Write a short, measured, professional "
    "plan: how to respond publicly if warranted, and how to request a correction or "
    "removal from the author or platform. Be specific and de-escalating. Return ONLY "
    "the plan text, with no preamble or commentary."
)


def _llm_suggestion(
    *,
    content: str,
    source: str | None,
    kind: str,
    analysis: AnalysisResult,
) -> FixSuggestion | None:
    """Try the configured LLM provider. Returns ``None`` to signal fallback.

    Wrapped so any failure (no LLM analyzer active, missing key, network, quota,
    empty/blank completion) degrades to the rule-based suggestion instead of
    raising — the caller must never 500 on this path.
    """
    try:
        analyzer = get_analyzer()
        # Only the LLM analyzer can call a provider; anything else -> fallback.
        call = getattr(analyzer, "_call_provider", None)
        if call is None or getattr(analyzer, "name", "") != "llm":
            return None

        system = _SYSTEM_REWRITE if kind == KIND_REWRITE else _SYSTEM_RESPONSE
        user_prompt = (
            f"{system}\n\n"
            f"Stored analysis — sentiment: {analysis.sentiment}, "
            f"risk_category: {analysis.risk_category}, risk_level: {analysis.risk_level}/5.\n"
            f"Source: {source}\n"
            f"Content:\n{content}"
        )
        text = call(user_prompt)
        suggestion = (text or "").strip()
        if not suggestion:
            return None

        rationale = _rationale(kind, analysis, llm=True)
        return FixSuggestion(kind=kind, suggestion=suggestion, rationale=rationale)
    except Exception:
        return None


# --- Rule-based fallback --------------------------------------------------
def _rule_based_suggestion(
    *,
    content: str,
    source: str | None,
    kind: str,
    analysis: AnalysisResult,
) -> FixSuggestion:
    if kind == KIND_REWRITE:
        suggestion = _rewrite_template(content, source, analysis)
    else:
        suggestion = _response_template(source, analysis)
    return FixSuggestion(
        kind=kind,
        suggestion=suggestion,
        rationale=_rationale(kind, analysis, llm=False),
    )


def _rewrite_template(content: str, source: str | None, analysis: AnalysisResult) -> str:
    """A calmer, factual rewrite scaffold for the user's own risky post."""
    platform = _platform_label(source)
    excerpt = (content or "").strip()
    if len(excerpt) > 240:
        excerpt = excerpt[:240].rstrip() + "…"

    lines = [
        f"Suggested safer rewrite for your {platform} post:",
        "",
        "\"I want to share an update and keep things constructive. "
        "Here's the situation as I see it, stated factually, and what I'd "
        "like to happen next. I'm open to discussing this directly.\"",
        "",
        "How to adapt it to your post:",
        "- Lead with the factual point you actually want to make.",
        "- Remove absolutes, name-calling, and anything you couldn't defend later.",
        "- Replace blame with a request or a next step.",
        "- Re-read it as if a future employer or client were reading it.",
    ]
    if excerpt:
        lines += ["", f"Your original (for reference): {excerpt}"]
    return "\n".join(lines)


def _response_template(source: str | None, analysis: AnalysisResult) -> str:
    """A polite correction / removal-request outline for a third-party mention."""
    category = analysis.risk_category if analysis.risk_category != "none" else "reputational"
    high_risk = analysis.risk_level >= 4

    lines = [
        "Suggested plan for this third-party mention:",
        "",
        "1. Decide whether to respond publicly. If the claim is factual and minor, "
        "a brief, calm correction can help; if it's inflammatory, often the best "
        "move is to address it privately and not amplify it.",
        "2. If you reply publicly, keep it short and factual:",
        "   \"Thanks for raising this. To clarify: [the accurate facts]. "
        "I'm happy to discuss directly.\"",
        "3. Contact the author or platform to request a correction or removal:",
        "   \"I'm the person referenced in this post. It contains "
        f"{category} information that is inaccurate/harmful. "
        "I'm requesting that you correct or remove it. Please let me know how to proceed.\"",
        "4. Document everything (URL, screenshot, date) before it changes.",
    ]
    if high_risk:
        lines.append(
            "5. Given the high risk level, consider escalating: the platform's "
            "formal reporting/legal channel, and PR or legal counsel if it spreads."
        )
    if analysis.recommendation:
        lines += ["", f"From the analysis: {analysis.recommendation}"]
    return "\n".join(lines)


def _rationale(kind: str, analysis: AnalysisResult, *, llm: bool) -> str:
    """One short sentence explaining why the suggestion helps, grounded in the analysis."""
    engine = "AI-generated" if llm else "Generated from the analysis"
    if kind == KIND_REWRITE:
        return (
            f"{engine}: this is your own post, flagged as {analysis.sentiment} with "
            f"{analysis.risk_category} risk at level {analysis.risk_level}/5. Editing it to a "
            "calmer, factual version directly lowers the reputational risk you control."
        )
    return (
        f"{engine}: this is third-party content you don't control, flagged as "
        f"{analysis.sentiment} with {analysis.risk_category} risk at level "
        f"{analysis.risk_level}/5. A measured correction or removal request is the "
        "safest way to limit its impact without escalating it."
    )
