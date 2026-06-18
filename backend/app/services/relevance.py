"""Relevance filter for brand/name mention scanning.

Decides whether a scanned mention's text is actually ABOUT the search
subject (a name / brand / handle), so broad keyless scans (DuckDuckGo,
Hacker News, ...) keep only real matches and drop fuzzy junk
("precourt", "prcount", "Supreme Court", "Michael Jordan", ...).

Strategy: normalized exact token / token-span matching (NO fuzzy edit
distance — fuzzy matching is what causes "pdrcourts"/"precourt" style
false positives, and false alerts are costly).

Normalization (applied to both query and text):
  - lowercase
  - Unicode NFKD + strip diacritics (so accented chars compare equal)
  - split on every non-alphanumeric run into word tokens
    -> "@pdrcourt's", "pdrcourt.com", "P.D.R. Court" all reduce cleanly.

Matching rules:
  Single-token query (e.g. "pdrcourt"):
    relevant iff the query equals
      (a) a whole text token, OR
      (b) a concatenation of one-or-more ADJACENT complete text tokens
          ("PDR Court" -> "pdr"+"court" == "pdrcourt").
    Because we compare COMPLETE tokens / token spans, a longer token like
    "precourt", "prcount", "court", "pdrcourtroom", or the plural
    "pdrcourts" never matches "pdrcourt".

  Multi-token query (e.g. "Jordan Demo"):
    relevant iff EVERY query token is present as a whole text token
    (order-independent), OR the query phrase appears as a consecutive run,
    OR the query collapses to a single brand token that matches the text
    via rule (a)/(b) above ("PDR Court" query vs "pdrcourt" text).
    "Michael Jordan" (missing 'demo') and "a demo of our product"
    (missing 'jordan') are both dropped.

  Empty / whitespace-only query -> relevant=True (no subject given, so the
  scan must not over-filter).

Stdlib only.
"""
from __future__ import annotations

import re
import unicodedata

_ALNUM_RUN = re.compile(r"[a-z0-9]+")

# Tokens that carry no identity in a multi-word name; ignored when present
# in a query so "Jordan & Demo" / "the Jordan Demo" still need jordan+demo.
_STOPWORDS = {
    "a", "an", "the", "of", "and", "or", "for", "to", "in", "on", "at",
    "by", "with", "is", "are", "was", "were", "be", "this", "that",
}


def _normalize(s: str) -> str:
    """Lowercase, strip accents, return space-joined alnum tokens.

    "PDR Court" -> "pdr court", "pdrcourt.com" -> "pdrcourt com",
    "@pdrcourt's" -> "pdrcourt s", "Beyonce" -> "beyonce".
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return " ".join(_ALNUM_RUN.findall(s.lower()))


def _tokens(s: str):
    """List of normalized word tokens."""
    n = _normalize(s)
    return n.split() if n else []


def _matches_token_span(text_tokens, q: str) -> bool:
    """True if `q` equals a concatenation of one or more COMPLETE adjacent
    text tokens.

    Defeats substring collisions: 'pdrcourt' must not match inside the
    single token 'precourt'/'prcount'/'pdrcourts'/'pdrcourtroom', and must
    not match the lone token 'court'. We only accept when accumulated whole
    tokens equal `q` exactly; we stop a window as soon as it overshoots.
    """
    n = len(text_tokens)
    for i in range(n):
        acc = ""
        for j in range(i, n):
            acc += text_tokens[j]
            if acc == q:
                return True
            if len(acc) > len(q):
                break
    return False


def _phrase_present(text_tokens, q_tokens) -> bool:
    """True if q_tokens appear as a consecutive run in text_tokens."""
    n, m = len(text_tokens), len(q_tokens)
    if m == 0 or m > n:
        return False
    for i in range(n - m + 1):
        if text_tokens[i:i + m] == q_tokens:
            return True
    return False


def _single_token_hit(text_tokens, q: str) -> bool:
    """Whole-token match OR styled-split (adjacent token span) match."""
    return q in text_tokens or _matches_token_span(text_tokens, q)


def relevance_score(query: str, text: str) -> float:
    """Return a 0.0..1.0 relevance score that `text` is about `query`."""
    q_tokens = _tokens(query)
    if not q_tokens:
        # No subject given -> never over-filter.
        return 1.0

    text_tokens = _tokens(text)

    # ---- Single-token query ---------------------------------------------
    if len(q_tokens) == 1:
        return 1.0 if _single_token_hit(text_tokens, q_tokens[0]) else 0.0

    # ---- Multi-token query ----------------------------------------------
    # (1) Whole query phrase appears consecutively.
    if _phrase_present(text_tokens, q_tokens):
        return 1.0

    # (2) The query collapses to one brand token that the text carries
    #     either whole or as a styled split ("PDR Court" query vs the
    #     collapsed "pdrcourt" text).
    collapsed_q = "".join(q_tokens)
    if _single_token_hit(text_tokens, collapsed_q):
        return 1.0

    # (3) Coverage: every significant query token present as a whole token.
    sig = [t for t in q_tokens if t not in _STOPWORDS] or q_tokens
    present = sum(1 for t in sig if t in text_tokens)
    if present == len(sig):
        return 1.0

    # Partial coverage stays below the default 0.6 threshold so a single
    # shared word (e.g. only "jordan" or only "demo") is dropped.
    return present / (len(sig) * 2.0)


def is_relevant(query: str, text: str, threshold: float = 0.6) -> bool:
    """Whether `text` is about `query`.

    Empty/whitespace query -> True (no subject -> don't over-filter).
    Single-token query -> exact normalized token / token-span match.
    Multi-token query -> all significant words present (so multi-word
    names like "Jordan Demo" require BOTH words).
    """
    if not _tokens(query):
        return True
    return relevance_score(query, text) >= threshold
