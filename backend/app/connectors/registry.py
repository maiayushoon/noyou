"""Connector registry — maps config names to connector instances."""
from __future__ import annotations

from ..core.config import settings
from .base import BaseConnector
from .demo import DemoConnector
from .free_web import (
    DuckDuckGoConnector,
    HackerNewsConnector,
    RedditPublicConnector,
)
from .news_rss import BingNewsConnector, GoogleNewsConnector
from .providers import (
    GoogleConnector,
    LinkedInConnector,
    RedditConnector,
    TwitterConnector,
    YouTubeConnector,
)

_REGISTRY: dict[str, type[BaseConnector]] = {
    DemoConnector.name: DemoConnector,
    # Keyless real-data connectors (work out of the box, no API keys):
    HackerNewsConnector.name: HackerNewsConnector,      # "hackernews"
    RedditPublicConnector.name: RedditPublicConnector,  # "reddit_public"
    DuckDuckGoConnector.name: DuckDuckGoConnector,       # "web"
    GoogleNewsConnector.name: GoogleNewsConnector,       # "googlenews" (keyless Google News RSS)
    BingNewsConnector.name: BingNewsConnector,           # "bing" (keyless Bing News RSS)
    # Keyed connectors (activate when credentials are configured):
    GoogleConnector.name: GoogleConnector,
    TwitterConnector.name: TwitterConnector,
    RedditConnector.name: RedditConnector,
    YouTubeConnector.name: YouTubeConnector,
    LinkedInConnector.name: LinkedInConnector,
}


def get_connector(name: str) -> BaseConnector | None:
    cls = _REGISTRY.get(name.lower())
    return cls() if cls else None


def get_active_connectors() -> list[BaseConnector]:
    """Instantiate the connectors named in config that are actually usable.

    If none of the configured connectors are usable (e.g. real ones lack keys), we
    always fall back to the demo connector so a scan still produces results.
    """
    active: list[BaseConnector] = []
    for name in settings.connector_list:
        conn = get_connector(name)
        if conn and conn.is_configured():
            active.append(conn)
    if not active:
        active.append(DemoConnector())
    return active
