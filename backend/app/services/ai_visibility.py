"""AI Visibility (GEO/AEO) assessment service.

Estimates how discoverable and representable a user's brand is to AI answer engines
(ChatGPT, Perplexity, Google AI Overviews, Gemini) from the signals we already have:
the user's scanned ``Mention``/``Analysis`` rows plus a few cheap heuristics. We score
each signal, combine the weighted signals into a 0-100 GEO score, bucket it into a
band, and emit concrete, tailored recommendations to improve AI visibility.

GEO/AEO best practice this service nudges toward: crawlable server-rendered HTML,
clear factual well-structured copy, FAQ content in real Q&A form, JSON-LD structured
data, an ``llms.txt``, consistent NAP/brand description across profiles, and getting
cited on third-party sources AI engines trust.

Everything here degrades gracefully — it must never raise — and stays on stdlib +
existing deps (httpx) only.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.analysis import Analysis
from ..models.mention import Mention
from ..models.user import User

# --- Tunable thresholds ---------------------------------------------------
MIN_SOURCE_DIVERSITY = 3          # distinct sources for the diversity signal
MIN_CONTENT_VOLUME = 5            # mentions for the volume signal
MIN_POSITIVE_RATIO = 0.4         # positive-sentiment share for the sentiment signal
HIGH_RISK_LEVEL = 4              # risk_level >= this counts as high-risk
RECENCY_DAYS = 30               # discovered_at within this window counts as recent

# Sources we treat as social platforms an AI engine can corroborate a brand against.
_SOCIAL_SOURCES = {
    "linkedin", "instagram", "twitter", "x", "youtube", "github",
    "facebook", "tiktok", "mastodon", "threads",
}

# Hosts that read as a brand's own/official presence rather than third-party coverage.
_OFFICIAL_TLDS = (".com", ".io", ".app", ".co", ".org", ".net", ".ai", ".dev")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _brand_for(user: User) -> str:
    """The primary brand label: the user's full name, else the local part of email."""
    name = (user.full_name or "").strip()
    if name:
        return name
    email = (user.email or "").strip()
    return email.split("@", 1)[0] if email else "your brand"


def _brand_tokens(brand: str) -> list[str]:
    """Lowercased alphanumeric tokens of the brand, for loose host matching."""
    cleaned = "".join(c if c.isalnum() else " " for c in brand.lower())
    return [t for t in cleaned.split() if len(t) >= 3]


def _band(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 65:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _host(url: str | None) -> str:
    if not url:
        return ""
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def assess(db: Session, user: User) -> dict:
    """Assess a user's AI visibility and return an ``AiVisibilityResponse``-shaped dict.

    Never raises: any unexpected failure falls back to a minimal, honest low-visibility
    assessment so the route can always return a 200.
    """
    try:
        return _assess(db, user)
    except Exception:
        brand = _brand_for(user)
        return {
            "brand": brand,
            "ai_visibility_score": 0.0,
            "band": "low",
            "signals": [],
            "recommendations": _baseline_recommendations(),
            "summary": (
                f"We couldn't fully assess {brand}'s AI visibility yet. Run a scan to "
                "gather mentions, then check back for a tailored GEO assessment."
            ),
            "llm_used": False,
        }


def _assess(db: Session, user: User) -> dict:
    brand = _brand_for(user)
    tokens = _brand_tokens(brand)

    # Pull the user's mentions joined to their analysis (analysis may be missing).
    rows = db.execute(
        select(Mention, Analysis)
        .outerjoin(Analysis, Analysis.mention_id == Mention.id)
        .where(Mention.user_id == user.id)
    ).all()

    total = len(rows)
    sources: set[str] = set()
    social_hits = 0
    official_hit = False
    positive = 0
    negative = 0
    analyzed = 0
    high_risk = False
    recent_hit = False
    recency_cutoff = _utcnow() - timedelta(days=RECENCY_DAYS)

    for mention, analysis in rows:
        source = (mention.source or "").lower()
        if source:
            sources.add(source)
        if source in _SOCIAL_SOURCES:
            social_hits += 1

        host = _host(mention.url)
        if host and not official_hit:
            # An official site: the brand name appears in the host, or the source is
            # the generic web connector pointing at a plausible brand domain.
            if any(tok in host for tok in tokens) or (
                source in {"web", "google"} and host.endswith(_OFFICIAL_TLDS)
                and any(tok in host for tok in tokens)
            ):
                official_hit = True

        if analysis is not None:
            analyzed += 1
            if analysis.sentiment == "positive":
                positive += 1
            elif analysis.sentiment == "negative":
                negative += 1
            if (analysis.risk_level or 0) >= HIGH_RISK_LEVEL:
                high_risk = True

        discovered = _aware(mention.discovered_at)
        if discovered and discovered >= recency_cutoff:
            recent_hit = True

    positive_ratio = (positive / analyzed) if analyzed else 0.0

    # --- Evaluate the weighted signals ------------------------------------
    signals: list[dict] = []

    signals.append({
        "name": "official_site_found",
        "present": official_hit,
        "weight": 22,
        "detail": (
            "An official/brand-owned page was found in your mentions — AI engines have a "
            "canonical source to describe you."
            if official_hit else
            "No clearly official brand page was found. AI engines may struggle to identify "
            "your canonical site."
        ),
    })

    has_social = social_hits > 0
    signals.append({
        "name": "social_presence",
        "present": has_social,
        "weight": 16,
        "detail": (
            f"Found {social_hits} mention(s) on social platforms (LinkedIn/Instagram/"
            "X/YouTube/GitHub) AI engines cross-reference."
            if has_social else
            "No social-platform mentions found. Active, consistent profiles help AI engines "
            "corroborate your brand."
        ),
    })

    diverse = len(sources) >= MIN_SOURCE_DIVERSITY
    signals.append({
        "name": "source_diversity",
        "present": diverse,
        "weight": 16,
        "detail": (
            f"Coverage spans {len(sources)} distinct source(s) — diverse, corroborating "
            "sources raise AI trust."
            if diverse else
            f"Only {len(sources)} source(s) found; aim for >= {MIN_SOURCE_DIVERSITY} so AI "
            "engines see corroboration, not a single voice."
        ),
    })

    enough_volume = total >= MIN_CONTENT_VOLUME
    signals.append({
        "name": "content_volume",
        "present": enough_volume,
        "weight": 12,
        "detail": (
            f"{total} mention(s) give AI engines enough material to summarize you."
            if enough_volume else
            f"Only {total} mention(s) found; more indexable content (>= {MIN_CONTENT_VOLUME}) "
            "gives AI engines something to quote."
        ),
    })

    good_sentiment = positive_ratio >= MIN_POSITIVE_RATIO
    signals.append({
        "name": "positive_sentiment_ratio",
        "present": good_sentiment,
        "weight": 12,
        "detail": (
            f"{round(positive_ratio * 100)}% of analyzed mentions are positive — favorable "
            "framing shapes how AI describes you."
            if good_sentiment else
            "Positive coverage is thin; favorable, factual content steers how AI engines "
            "characterize your brand."
        ),
    })

    low_risk = not high_risk
    signals.append({
        "name": "low_risk",
        "present": low_risk,
        "weight": 12,
        "detail": (
            "No high-risk content detected — nothing reputationally damaging for an AI to "
            "surface."
            if low_risk else
            "High-risk content was detected; address it before it gets surfaced in AI answers."
        ),
    })

    signals.append({
        "name": "recency",
        "present": recent_hit,
        "weight": 10,
        "detail": (
            f"Fresh activity within the last {RECENCY_DAYS} days keeps your AI footprint "
            "current."
            if recent_hit else
            f"No mentions in the last {RECENCY_DAYS} days; recent activity signals an active, "
            "describable brand."
        ),
    })

    # --- Weighted score ----------------------------------------------------
    weight_total = sum(s["weight"] for s in signals)
    earned = sum(s["weight"] for s in signals if s["present"])
    score = round(100.0 * earned / weight_total, 1) if weight_total else 0.0
    band = _band(score)

    recommendations = _recommendations(signals, brand)
    summary = _heuristic_summary(brand, score, band, total)

    # --- Optional LLM enrichment (graceful) --------------------------------
    llm_used = False
    if _llm_configured():
        described = _llm_describe_brand(brand)
        if described:
            summary = f"{summary} How an AI engine might describe you today: \"{described}\""
            llm_used = True

    return {
        "brand": brand,
        "ai_visibility_score": score,
        "band": band,
        "signals": signals,
        "recommendations": recommendations,
        "summary": summary,
        "llm_used": llm_used,
    }


def _baseline_recommendations() -> list[str]:
    """GEO foundations every brand should have, used when we have little/no data."""
    return [
        "Publish a server-rendered, crawlable site with clear, factual copy AI engines can read without JavaScript.",
        "Add an llms.txt (and llms-full.txt) to your site so LLMs know what you are and which pages matter.",
        "Add JSON-LD structured data (Organization, WebSite, SoftwareApplication, FAQPage) so AI engines can parse you.",
        "Publish an FAQ page in real Q&A format with FAQPage schema so AI engines can quote you directly.",
        "Keep your NAP and brand description consistent across every profile so AI engines resolve one identity.",
    ]


def _recommendations(signals: list[dict], brand: str) -> list[str]:
    """Concrete, tailored GEO recommendations driven by the missing signals."""
    by_name = {s["name"]: s for s in signals}
    recs: list[str] = []

    if not by_name["official_site_found"]["present"]:
        recs.append(
            "Stand up a canonical, server-rendered site for your brand and add an llms.txt + "
            "JSON-LD Organization schema so AI engines can identify your official source."
        )
    if not by_name["social_presence"]["present"]:
        recs.append(
            "Activate and cross-link consistent profiles on LinkedIn, X, YouTube, and GitHub so "
            "AI engines can corroborate your brand across platforms."
        )
    else:
        recs.append(
            "Keep your dormant or sparse social profiles active and consistent (same name, bio, "
            "and links) so AI engines see one coherent identity."
        )
    if not by_name["source_diversity"]["present"]:
        recs.append(
            "Get cited on third-party sources AI engines trust — news, industry blogs, wikis, and "
            "directories — so your brand isn't represented by a single voice."
        )
    if not by_name["content_volume"]["present"]:
        recs.append(
            "Publish more indexable, well-structured content (definitions, how-tos, FAQs) so AI "
            "answer engines have material to surface and quote."
        )
    if not by_name["positive_sentiment_ratio"]["present"]:
        recs.append(
            "Seed favorable, factual coverage (case studies, testimonials, founder commentary) to "
            "shape how AI engines frame your brand."
        )
    if not by_name["low_risk"]["present"]:
        recs.append(
            "Address high-risk content first — request removal or publish authoritative responses — "
            "so it isn't what AI engines surface about you."
        )
    if not by_name["recency"]["present"]:
        recs.append(
            "Publish fresh content regularly; recency signals an active brand and keeps your AI "
            "footprint current."
        )

    # Always include the universally-applicable GEO best practices.
    recs.append(
        "Publish an FAQ page in genuine Q&A format with FAQPage schema so AI engines can lift "
        "direct answers about you."
    )
    recs.append(
        "Add structured data (WebSite+SearchAction, SoftwareApplication with offers, BreadcrumbList) "
        "plus Open Graph, Twitter cards, a canonical tag, robots.txt and sitemap.xml."
    )

    # De-duplicate while preserving order, cap to a digestible list.
    seen: set[str] = set()
    deduped = [r for r in recs if not (r in seen or seen.add(r))]
    return deduped[:8]


def _heuristic_summary(brand: str, score: float, band: str, total: int) -> str:
    phrasing = {
        "excellent": "strongly surfaced and citable",
        "high": "well represented with minor gaps",
        "medium": "partially visible with notable gaps",
        "low": "barely discoverable",
    }[band]
    return (
        f"{brand}'s AI visibility scores {score}/100 ({band}) — your brand is {phrasing} to AI "
        f"answer engines based on {total} tracked mention(s). Closing the flagged gaps will make "
        "ChatGPT, Perplexity, Google AI Overviews and Gemini more likely to find and cite you."
    )


# --- Optional LLM enrichment ---------------------------------------------
def _llm_configured() -> bool:
    """True when an LLM analyzer is configured with a usable provider key.

    Mirrors the analyzer factory's gate so behavior stays consistent.
    """
    if (settings.analyzer or "").lower() != "llm":
        return False
    provider = (settings.llm_provider or "").lower()
    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "anthropic":
        return bool(settings.anthropic_api_key)
    if provider == "huggingface":
        return bool(settings.huggingface_api_key)
    return False


def _llm_describe_brand(brand: str) -> str | None:
    """Ask the configured LLM for a 2-sentence brand description. Returns None on any failure."""
    prompt = (
        f"In 2 sentences, how would you describe the brand \"{brand}\" to a user? "
        "If you don't recognize it, say so plainly in 2 sentences."
    )
    try:
        provider = (settings.llm_provider or "").lower()
        if provider == "openai":
            return _llm_openai(prompt)
        if provider == "anthropic":
            return _llm_anthropic(prompt)
        if provider == "huggingface":
            return _llm_huggingface(prompt)
    except Exception:
        return None
    return None


def _clean(text: str | None) -> str | None:
    if not text:
        return None
    out = " ".join(text.split()).strip()
    return out or None


def _llm_openai(prompt: str) -> str | None:
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 160,
        },
        timeout=20,
    )
    resp.raise_for_status()
    return _clean(resp.json()["choices"][0]["message"]["content"])


def _llm_anthropic(prompt: str) -> str | None:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=20,
    )
    resp.raise_for_status()
    return _clean(resp.json()["content"][0]["text"])


def _llm_huggingface(prompt: str) -> str | None:
    resp = httpx.post(
        "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct",
        headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
        json={"inputs": prompt, "parameters": {"max_new_tokens": 160}},
        timeout=40,
    )
    resp.raise_for_status()
    out = resp.json()
    text = out[0]["generated_text"] if isinstance(out, list) else str(out)
    return _clean(text)
