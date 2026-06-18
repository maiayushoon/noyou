"""Lexicons powering the offline analyzer.

This is intentionally data, not code: it's the knob you tune for accuracy without
touching logic, and it's the natural place to plug a learned model later. Weights
are rough but produce sensible, explainable results across the demo corpus.
"""
from __future__ import annotations

# --- Sentiment ---------------------------------------------------------------
POSITIVE_WORDS: dict[str, float] = {
    "excellent": 1.0, "amazing": 1.0, "outstanding": 1.0, "great": 0.8, "love": 0.9,
    "loved": 0.9, "fantastic": 1.0, "wonderful": 0.9, "best": 0.8, "brilliant": 0.9,
    "talented": 0.8, "professional": 0.6, "helpful": 0.7, "impressive": 0.8,
    "recommend": 0.7, "recommended": 0.7, "inspiring": 0.8, "kind": 0.6, "award": 0.7,
    "awarded": 0.7, "praised": 0.8, "respected": 0.7, "trusted": 0.7, "success": 0.7,
    "successful": 0.7, "thank": 0.5, "thanks": 0.5, "congrats": 0.7, "congratulations": 0.7,
    "leader": 0.6, "expert": 0.6, "innovative": 0.7, "reliable": 0.6, "good": 0.5,
}

NEGATIVE_WORDS: dict[str, float] = {
    "scam": 1.0, "fraud": 1.0, "fraudulent": 1.0, "liar": 1.0, "lied": 0.9, "lying": 0.9,
    "terrible": 0.9, "awful": 0.9, "horrible": 0.9, "worst": 0.9, "hate": 0.9, "disgusting": 0.9,
    "incompetent": 0.9, "unprofessional": 0.9, "rude": 0.7, "dishonest": 0.9, "corrupt": 1.0,
    "abuse": 0.9, "abusive": 0.9, "harassment": 1.0, "harass": 0.9, "toxic": 0.8, "shady": 0.8,
    "avoid": 0.7, "warning": 0.6, "disappointed": 0.7, "disappointing": 0.7, "fail": 0.6,
    "failed": 0.6, "failure": 0.7, "lawsuit": 0.8, "sued": 0.8, "arrested": 1.0, "guilty": 0.9,
    "fired": 0.7, "racist": 1.0, "sexist": 1.0, "fake": 0.7, "cheat": 0.9, "cheated": 0.9,
    "stole": 0.9, "theft": 0.9, "complaint": 0.6, "refund": 0.5, "ripoff": 0.9, "negligent": 0.8,
    "unreliable": 0.7, "bad": 0.5, "poor": 0.5, "ignored": 0.5, "danger": 0.7, "dangerous": 0.8,
}

NEGATORS = {"not", "no", "never", "none", "nothing", "isn't", "wasn't", "aren't", "weren't", "don't", "didn't", "can't"}
INTENSIFIERS = {"very": 1.4, "extremely": 1.7, "really": 1.3, "so": 1.2, "highly": 1.4, "totally": 1.4, "absolutely": 1.6}

# --- Risk categories ---------------------------------------------------------
# Each keyword maps to (category, base_risk 1..5). Higher = more damaging.
RISK_KEYWORDS: dict[str, tuple[str, int]] = {
    # career / professional reputation
    "fired": ("career", 4), "incompetent": ("career", 4), "unprofessional": ("career", 3),
    "scandal": ("career", 5), "misconduct": ("career", 5), "plagiarism": ("career", 4),
    "demoted": ("career", 3), "resigned": ("career", 2), "underperforming": ("career", 3),
    "blacklisted": ("career", 4),
    # legal
    "lawsuit": ("legal", 5), "sued": ("legal", 5), "arrested": ("legal", 5), "guilty": ("legal", 5),
    "convicted": ("legal", 5), "fraud": ("legal", 5), "illegal": ("legal", 4), "criminal": ("legal", 5),
    "subpoena": ("legal", 4), "indicted": ("legal", 5), "settlement": ("legal", 3),
    # financial
    "bankruptcy": ("financial", 4), "bankrupt": ("financial", 4), "debt": ("financial", 3),
    "scam": ("financial", 5), "ponzi": ("financial", 5), "embezzle": ("financial", 5),
    "unpaid": ("financial", 3), "default": ("financial", 3), "refund": ("financial", 2),
    # privacy / doxxing
    "address": ("privacy", 3), "phone number": ("privacy", 4), "home address": ("privacy", 5),
    "ssn": ("privacy", 5), "leaked": ("privacy", 4), "doxxed": ("privacy", 5), "doxx": ("privacy", 5),
    "private photos": ("privacy", 5), "personal data": ("privacy", 4), "exposed": ("privacy", 3),
    # personal / character
    "racist": ("personal", 5), "sexist": ("personal", 5), "harassment": ("personal", 5),
    "abuse": ("personal", 5), "abusive": ("personal", 4), "bully": ("personal", 4),
    "affair": ("personal", 3), "drunk": ("personal", 2), "addiction": ("personal", 3),
    "toxic": ("personal", 3), "cheat": ("personal", 3), "liar": ("personal", 3),
}

# Phrases that signal a *positive* or neutral context even if risk words appear,
# used to soften false positives (e.g. news the subject was the victim/whistleblower).
CONTEXT_SOFTENERS = (
    "award", "charity", "volunteer", "fundraiser", "donated", "keynote", "speaker",
    "promoted", "hired", "launched", "published", "featured",
)
