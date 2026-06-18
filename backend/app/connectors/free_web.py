"""Keyless, best-effort REAL data connectors.

These connectors pull genuine web and social mentions **without any API keys**, so
the public-facing product surfaces real data out of the box. They hit free, public
endpoints (Algolia's Hacker News search, Reddit's public ``.json`` views, and the
DuckDuckGo HTML page), parse what comes back, and normalize it into ``RawMention``
records like every other connector.

Caveats — read before relying on these in volume:
  * They are **best-effort** and **unauthenticated**, so they may be **rate-limited**
    (HTTP 429), throttled, or change shape without notice. Every network call is
    wrapped: on *any* failure a connector returns ``[]`` instead of raising, so a
    flaky source degrades the scan gracefully rather than breaking it.
  * For high-volume, reliable web search the recommended source is Google Custom
    Search (``GoogleConnector`` in ``providers.py``): the free tier allows 100
    queries/day with a real API key and is far more stable than HTML scraping.

Set ``CONNECTORS=web,hackernews,reddit_public,demo`` to run on real data with the
demo connector as a guaranteed fallback.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from .base import BaseConnector, RawMention

# A descriptive User-Agent is required by Reddit (and polite for the others) — a
# generic or empty UA gets aggressively rate-limited / blocked with HTTP 429.
_USER_AGENT = "noyou/1.0 reputation-monitor (+https://noyou.app)"
# DuckDuckGo's HTML endpoint expects a browser-like UA or it returns an empty page.
_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_TIMEOUT = 20

# Strip a basic set of HTML tags / entities from API-supplied snippets. These are
# deliberately small and tolerant — we want readable plain text, not a parser.
_TAG_RE = re.compile(r"<[^>]+>")
_ENTITIES = {
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#x27;": "'",
    "&#39;": "'",
    "&nbsp;": " ",
}


def _safe_get(url: str, **kwargs) -> httpx.Response | None:
    """GET a URL, returning the response or ``None`` on any error (incl. 4xx/5xx)."""
    try:
        resp = httpx.get(url, timeout=_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception:
        return None


def _safe_post(url: str, **kwargs) -> httpx.Response | None:
    """POST to a URL, returning the response or ``None`` on any error."""
    try:
        resp = httpx.post(url, timeout=_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception:
        return None


def _strip_html(value: str | None) -> str:
    """Best-effort plain-text from an HTML-ish snippet (tags + common entities)."""
    if not value:
        return ""
    text = _TAG_RE.sub("", value)
    for entity, char in _ENTITIES.items():
        text = text.replace(entity, char)
    return text.strip()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _parse_epoch(value) -> datetime | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError):
        return None


class HackerNewsConnector(BaseConnector):
    """Hacker News stories + comments via the free, keyless Algolia HN search API."""

    name = "hackernews"
    label = "Hacker News"

    def is_configured(self) -> bool:
        return True

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        resp = _safe_get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": query,
                "tags": "(story,comment)",
                "hitsPerPage": max(1, min(limit, 100)),
            },
        )
        if resp is None:
            return []
        try:
            data = resp.json()
        except Exception:
            return []

        out: list[RawMention] = []
        for hit in data.get("hits", []):
            object_id = hit.get("objectID")
            if not object_id:
                continue
            # Stories carry ``title``/``story_text``; comments carry ``comment_text``.
            content = _strip_html(
                hit.get("title") or hit.get("comment_text") or hit.get("story_text") or ""
            )
            published_at = _parse_epoch(hit.get("created_at_i")) or _parse_iso(
                hit.get("created_at")
            )
            out.append(
                RawMention(
                    source=self.name,
                    external_id=str(object_id),
                    content=content,
                    title=_strip_html(hit.get("title")) or None,
                    url=f"https://news.ycombinator.com/item?id={object_id}",
                    author=hit.get("author"),
                    published_at=published_at,
                    extra={"points": hit.get("points"), "num_comments": hit.get("num_comments")},
                )
            )
        return out


class RedditPublicConnector(BaseConnector):
    """Reddit search via the keyless public ``search.json`` endpoint.

    No OAuth required — this is the same JSON Reddit serves to the public web. It
    *will* return HTTP 429 without a descriptive User-Agent, and may be throttled
    regardless; both cases degrade to an empty result.
    """

    name = "reddit_public"
    label = "Reddit (public)"

    def is_configured(self) -> bool:
        return True

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        resp = _safe_get(
            "https://www.reddit.com/search.json",
            headers={"User-Agent": _USER_AGENT},
            params={
                "q": query,
                "limit": max(1, min(limit, 100)),
                "sort": "new",
            },
        )
        if resp is None:
            return []
        try:
            data = resp.json()
        except Exception:
            return []

        out: list[RawMention] = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            post_id = d.get("id")
            if not post_id:
                continue
            permalink = d.get("permalink", "")
            out.append(
                RawMention(
                    source=self.name,
                    external_id=str(post_id),
                    content=d.get("selftext") or d.get("title", ""),
                    title=d.get("title"),
                    url=("https://reddit.com" + permalink) if permalink else d.get("url"),
                    author=d.get("author"),
                    published_at=_parse_epoch(d.get("created_utc")),
                    extra={"subreddit": d.get("subreddit"), "score": d.get("score")},
                )
            )
        return out


class DuckDuckGoConnector(BaseConnector):
    """Best-effort keyless web search via DuckDuckGo's HTML endpoint.

    This scrapes the lightweight HTML results page with a small ``re`` parse (no
    bs4 dependency). It is inherently fragile — DDG may change its markup or rate
    limit — so it always degrades to ``[]`` rather than raising. For dependable,
    higher-volume web search, prefer ``GoogleConnector`` (free 100 queries/day).
    """

    name = "web"
    label = "Web (DuckDuckGo)"

    # Each organic result link, e.g. <a ... class="result__a" href="...">Title</a>.
    _RESULT_LINK_RE = re.compile(
        r'<a[^>]+class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    # The snippet block that typically follows a result link.
    _SNIPPET_RE = re.compile(
        r'<a[^>]+class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )

    def is_configured(self) -> bool:
        return True

    @staticmethod
    def _decode_href(href: str) -> str:
        """Resolve DDG's redirect wrapper (``/l/?uddg=<urlencoded>``) to the real URL."""
        if not href:
            return ""
        # Protocol-relative wrapper links arrive as //duckduckgo.com/l/?uddg=...
        candidate = href
        if candidate.startswith("//"):
            candidate = "https:" + candidate
        try:
            parsed = urlparse(candidate)
        except ValueError:
            return href
        if "/l/" in parsed.path:
            target = parse_qs(parsed.query).get("uddg", [])
            if target:
                return unquote(target[0])
        return href

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        resp = _safe_post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": _BROWSER_USER_AGENT},
        )
        if resp is None:
            return []
        try:
            html = resp.text
        except Exception:
            return []

        # Pair up result links with the snippet that follows each one. Snippets are
        # optional, so we match links positionally and grab the next snippet in order.
        snippets = [m.group("snippet") for m in self._SNIPPET_RE.finditer(html)]

        out: list[RawMention] = []
        for idx, match in enumerate(self._RESULT_LINK_RE.finditer(html)):
            if len(out) >= limit:
                break
            url = self._decode_href(match.group("href"))
            if not url:
                continue
            title = _strip_html(match.group("title"))
            snippet = _strip_html(snippets[idx]) if idx < len(snippets) else ""
            content = snippet or title
            if not content:
                continue
            # The redirect href isn't stable, but the resolved target URL is — hash it
            # for a deterministic external_id usable for de-duplication.
            external_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
            out.append(
                RawMention(
                    source=self.name,
                    external_id=external_id,
                    content=content,
                    title=title or None,
                    url=url,
                    author=urlparse(url).netloc or None,
                )
            )
        return out
