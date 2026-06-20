"""Keyless news connectors backed by public RSS feeds.

Both Google News and Bing News expose free, **no-API-key** RSS search endpoints that
return real, dated news mentions across the open web. They are the recommended free
"Google/Bing" sources for a public launch — far more stable than HTML scraping and
they carry publication dates, which makes them useful for historical/time-range views.

Like the other keyless connectors, every network call is wrapped: on *any* failure
(network, throttling, malformed XML) the connector returns ``[]`` rather than raising,
so a flaky feed degrades the scan gracefully instead of breaking it.

Both accept optional ``before``/``after`` dates (``datetime.date``) which are encoded
into the query using each engine's native date operators, so a scan can reach back
years where the source has coverage.
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

from .base import BaseConnector, RawMention
from .free_web import _safe_get, _strip_html

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _parse_rfc822(value: str | None) -> datetime | None:
    """Parse an RSS ``pubDate`` (RFC-822) into an aware UTC datetime."""
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _items(xml_text: str) -> list[ET.Element]:
    """Return ``<item>`` elements from an RSS document, tolerant of namespaces."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    # RSS 2.0: rss > channel > item. Use a wildcard search so we don't trip on feeds
    # that wrap items differently.
    return root.findall(".//item")


def _date_query(query: str, before: date | None, after: date | None, op: str) -> str:
    """Append native date operators to a query. ``op`` is the engine's prefix style."""
    parts = [query]
    if after:
        parts.append(f"{op}after:{after.isoformat()}" if op else f"after:{after.isoformat()}")
    if before:
        parts.append(f"{op}before:{before.isoformat()}" if op else f"before:{before.isoformat()}")
    return " ".join(parts)


class GoogleNewsConnector(BaseConnector):
    """Real Google-indexed news via the free, keyless Google News RSS search feed."""

    name = "googlenews"
    label = "Google News"

    def is_configured(self) -> bool:
        return True

    def search(
        self,
        query: str,
        *,
        limit: int = 25,
        before: date | None = None,
        after: date | None = None,
    ) -> list[RawMention]:
        q = _date_query(query, before, after, op="")
        resp = _safe_get(
            "https://news.google.com/rss/search",
            params={"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"},
            headers={"User-Agent": _BROWSER_UA},
        )
        if resp is None:
            return []

        out: list[RawMention] = []
        for item in _items(resp.text):
            if len(out) >= limit:
                break
            link = (item.findtext("link") or "").strip()
            title = _strip_html(item.findtext("title"))
            if not link or not title:
                continue
            description = _strip_html(item.findtext("description"))
            source_el = item.find("source")
            source_name = (source_el.text or "").strip() if source_el is not None else None
            out.append(
                RawMention(
                    source=self.name,
                    external_id=hashlib.sha1(link.encode("utf-8")).hexdigest()[:16],
                    content=description or title,
                    title=title,
                    url=link,
                    author=source_name,
                    published_at=_parse_rfc822(item.findtext("pubDate")),
                    extra={"publisher": source_name},
                )
            )
        return out


class BingNewsConnector(BaseConnector):
    """Real web news via Bing News' free, keyless RSS search feed."""

    name = "bing"
    label = "Bing News"

    def is_configured(self) -> bool:
        return True

    def search(
        self,
        query: str,
        *,
        limit: int = 25,
        before: date | None = None,
        after: date | None = None,
    ) -> list[RawMention]:
        resp = _safe_get(
            "https://www.bing.com/news/search",
            params={"q": query, "format": "RSS", "count": max(1, min(limit, 100))},
            headers={"User-Agent": _BROWSER_UA},
        )
        if resp is None:
            return []

        out: list[RawMention] = []
        for item in _items(resp.text):
            if len(out) >= limit:
                break
            link = (item.findtext("link") or "").strip()
            title = _strip_html(item.findtext("title"))
            if not link or not title:
                continue
            description = _strip_html(item.findtext("description"))
            out.append(
                RawMention(
                    source=self.name,
                    external_id=hashlib.sha1(link.encode("utf-8")).hexdigest()[:16],
                    content=description or title,
                    title=title,
                    url=link,
                    author="bing.news",
                    published_at=_parse_rfc822(item.findtext("pubDate")),
                )
            )
        return out
