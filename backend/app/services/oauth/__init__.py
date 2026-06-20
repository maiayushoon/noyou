"""OAuth provider registry for the Connections feature.

Maps a provider name to its :class:`~app.services.oauth.base.OAuthProvider`
singleton. The Connections router and the owned-content connector resolve adapters
exclusively through :func:`get_provider` / :func:`list_providers`, so wiring a new
platform is: add its class, register it here.

Wire order favors no-approval easy wins first: Mastodon, YouTube, Reddit, then the
Meta providers Threads and Instagram.
"""
from __future__ import annotations

from .base import Identity, OAuthProvider, TokenBundle
from .instagram import InstagramProvider
from .mastodon import MastodonProvider
from .reddit import RedditProvider
from .threads import ThreadsProvider
from .youtube import YouTubeProvider

# Insertion order is the UI/wire order.
_PROVIDERS: dict[str, OAuthProvider] = {
    p.name: p
    for p in (
        MastodonProvider(),
        YouTubeProvider(),
        RedditProvider(),
        ThreadsProvider(),
        InstagramProvider(),
    )
}


def get_provider(name: str) -> OAuthProvider | None:
    """Return the provider adapter for ``name`` (case-insensitive), or ``None``."""
    if not name:
        return None
    return _PROVIDERS.get(name.strip().lower())


def list_providers() -> list[OAuthProvider]:
    """Return all registered provider adapters in wire order."""
    return list(_PROVIDERS.values())


__all__ = [
    "Identity",
    "OAuthProvider",
    "TokenBundle",
    "get_provider",
    "list_providers",
]
