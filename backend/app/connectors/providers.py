"""Real-source connectors (Google, X/Twitter, Reddit, YouTube, LinkedIn).

Each is a *working skeleton*: the HTTP shape is correct, but they only activate when
their credentials are configured (``is_configured()``). Until then the registry
skips them, so the app runs on the demo connector alone. Fill in keys → real data,
no other code changes. Network calls are wrapped so a failing provider degrades to
an empty result instead of breaking the whole scan.
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..core.config import settings
from .base import BaseConnector, RawMention


def _safe_get(url: str, **kwargs) -> dict | None:
    try:
        resp = httpx.get(url, timeout=20, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def _safe_post(url: str, **kwargs) -> dict | None:
    try:
        resp = httpx.post(url, timeout=20, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


class GoogleConnector(BaseConnector):
    name = "google"
    label = "Google Search"

    def is_configured(self) -> bool:
        return bool(settings.google_api_key and settings.google_cse_id)

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        data = _safe_get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": settings.google_api_key,
                "cx": settings.google_cse_id,
                "q": query,
                "num": min(limit, 10),
            },
        )
        if not data:
            return []
        out: list[RawMention] = []
        for item in data.get("items", []):
            out.append(
                RawMention(
                    source="google",
                    external_id=item.get("cacheId") or item.get("link", ""),
                    content=item.get("snippet", ""),
                    title=item.get("title"),
                    url=item.get("link"),
                    author=item.get("displayLink"),
                )
            )
        return out


class TwitterConnector(BaseConnector):
    name = "twitter"
    label = "X / Twitter"

    def is_configured(self) -> bool:
        return bool(settings.twitter_bearer_token)

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        data = _safe_get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers={"Authorization": f"Bearer {settings.twitter_bearer_token}"},
            params={
                "query": query,
                "max_results": min(max(limit, 10), 100),
                "tweet.fields": "created_at,author_id,public_metrics",
            },
        )
        if not data:
            return []
        out: list[RawMention] = []
        for t in data.get("data", []):
            out.append(
                RawMention(
                    source="twitter",
                    external_id=t["id"],
                    content=t.get("text", ""),
                    url=f"https://twitter.com/i/web/status/{t['id']}",
                    author=t.get("author_id"),
                    published_at=_parse_iso(t.get("created_at")),
                )
            )
        return out


class RedditConnector(BaseConnector):
    name = "reddit"
    label = "Reddit"

    def is_configured(self) -> bool:
        return bool(settings.reddit_client_id and settings.reddit_client_secret)

    def _token(self) -> str | None:
        data = _safe_post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(settings.reddit_client_id, settings.reddit_client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": settings.reddit_user_agent},
        )
        return data.get("access_token") if data else None

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        token = self._token()
        if not token:
            return []
        data = _safe_get(
            "https://oauth.reddit.com/search",
            headers={"Authorization": f"Bearer {token}", "User-Agent": settings.reddit_user_agent},
            params={"q": query, "limit": limit, "sort": "new"},
        )
        if not data:
            return []
        out: list[RawMention] = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            out.append(
                RawMention(
                    source="reddit",
                    external_id=d.get("id", ""),
                    content=d.get("selftext") or d.get("title", ""),
                    title=d.get("title"),
                    url="https://reddit.com" + d.get("permalink", ""),
                    author=d.get("author"),
                    published_at=_parse_epoch(d.get("created_utc")),
                )
            )
        return out


class YouTubeConnector(BaseConnector):
    name = "youtube"
    label = "YouTube"

    def is_configured(self) -> bool:
        return bool(settings.youtube_api_key)

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        data = _safe_get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": settings.youtube_api_key,
                "q": query,
                "part": "snippet",
                "maxResults": min(limit, 50),
                "type": "video",
            },
        )
        if not data:
            return []
        out: list[RawMention] = []
        for item in data.get("items", []):
            vid = item.get("id", {}).get("videoId", "")
            sn = item.get("snippet", {})
            out.append(
                RawMention(
                    source="youtube",
                    external_id=vid,
                    content=sn.get("description", ""),
                    title=sn.get("title"),
                    url=f"https://youtube.com/watch?v={vid}",
                    author=sn.get("channelTitle"),
                    published_at=_parse_iso(sn.get("publishedAt")),
                )
            )
        return out


class LinkedInConnector(BaseConnector):
    """LinkedIn has no open search API; this requires partner access / OAuth.

    Left as a configured-by-token stub so the integration point exists. Until LinkedIn
    partner credentials are wired, it reports unconfigured and is skipped.
    """

    name = "linkedin"
    label = "LinkedIn"

    def is_configured(self) -> bool:
        return False  # requires LinkedIn Marketing/Partner API approval

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        return []


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_epoch(value) -> datetime | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError):
        return None
