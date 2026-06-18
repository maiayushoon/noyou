"""Tests for the brand/name relevance filter.

The 15-row FIXED ORACLE must pass exactly: the matcher keeps real matches
(styled handles, multi-word names) and drops fuzzy junk ("precourt",
"prcount", "Supreme Court", "Michael Jordan", a bare "demo", ...).
"""
from __future__ import annotations

import pytest

from app.services.relevance import _normalize, is_relevant, relevance_score

# [query, text, expected_relevant] — every row MUST match.
ORACLE = [
    ("pdrcourt", "Welcome to pdrcourt.com - your reputation portal", True),
    ("pdrcourt", "Had a great experience with PDRCourt support team", True),
    ("pdrcourt", "Follow @pdrcourt for updates", True),
    ("pdrcourt", "PDR Court handled my case professionally", True),
    ("pdrcourt", "pdrcourt's new website launched today", True),
    ("Jordan Demo", "Jordan Demo delivered an inspiring keynote", True),
    ("Jordan Demo", "I finally met Jordan Demo at the conference", True),
    ("pdrcourt", "The Stanford Precourt Institute for Energy", False),
    ("pdrcourt", "Creator of prcount.com here, thanks for the feedback", False),
    ("pdrcourt", "Man fined $120 for using Apple Watch while driving", False),
    ("pdrcourt", "Modell's name is a curse word in Cleveland", False),
    ("pdrcourt", "The Supreme Court ruled on the case today", False),
    ("pdrcourt", "Pull request and commit analytics for teams", False),
    ("Jordan Demo", "Michael Jordan played basketball for the Bulls", False),
    ("Jordan Demo", "Here is a quick demo of our new product", False),
]


@pytest.mark.parametrize("query,text,expected", ORACLE)
def test_oracle(query: str, text: str, expected: bool):
    assert is_relevant(query, text) is expected


# ---- Extra edge cases ----------------------------------------------------

def test_empty_query_never_over_filters():
    # No subject given -> must not drop anything.
    assert is_relevant("", "literally anything at all") is True
    assert is_relevant("   ", "another mention") is True


def test_styled_query_collapses_to_brand_token():
    # Multi-token query that collapses to the brand the text carries.
    assert is_relevant("PDR Court", "love pdrcourt so much") is True
    assert is_relevant("pdr court", "the pdrcourt.com portal") is True


def test_accents_and_case_are_normalized():
    assert is_relevant("Beyonce", "Beyoncé dropped a new album") is True
    assert is_relevant("BEYONCE", "a beyonce fan account") is True


def test_plural_and_substring_do_not_match_single_token():
    # Longer/plural tokens must NOT match the exact brand.
    assert is_relevant("pdrcourt", "check out pdrcourts and friends") is False
    assert is_relevant("pdrcourt", "the pdrcourtroom was packed") is False


def test_multiword_requires_all_significant_words():
    # Only one of the two words present -> dropped.
    assert is_relevant("Jordan Demo", "Jordan went to the store") is False
    assert is_relevant("Jordan Demo", "watch the demo replay") is False
    # Both present, any order -> kept.
    assert is_relevant("Jordan Demo", "a demo featuring Jordan herself") is True


def test_normalize_basic():
    assert _normalize("@pdrcourt's") == "pdrcourt s"
    assert _normalize("P.D.R. Court") == "p d r court"
    assert _normalize("") == ""


def test_score_bounds():
    assert relevance_score("pdrcourt", "welcome to pdrcourt") == 1.0
    assert relevance_score("pdrcourt", "unrelated text here") == 0.0
