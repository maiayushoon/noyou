"""The OAuth provider contract and shared, never-raising HTTP helpers.

Every connectable platform (Mastodon, YouTube/Google, Reddit, Threads, Instagram,
and later X/TikTok) implements :class:`OAuthProvider`. The Connections router and
the owned-content connector talk only to this interface, so adding a provider is:
write one subclass, register it in ``services/oauth/__init__.py``.

All network calls go through :func:`safe_request` / :func:`safe_get` /
:func:`safe_post`, which mirror ``connectors/free_web.py``'s ``_safe_get``: on ANY
error they return ``None`` instead of raising, so a flaky/expired provider degrades
a scan gracefully instead of breaking it. Tokens are passed as call-time
Authorization headers and never logged.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import httpx

from ...connectors.base import RawMention

_TIMEOUT = 20


def safe_request(method: str, url: str, **kwargs) -> httpx.Response | None:
    """Perform an HTTP request, returning the response or ``None`` on ANY error.

    Never raises. Never logs request bodies, params, or headers (which may carry
    tokens). 4xx/5xx are treated as failures (``raise_for_status``) and swallowed.
    """
    kwargs.setdefault("timeout", _TIMEOUT)
    try:
        resp = httpx.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception:
        return None


def safe_get(url: str, **kwargs) -> httpx.Response | None:
    return safe_request("GET", url, **kwargs)


def safe_post(url: str, **kwargs) -> httpx.Response | None:
    return safe_request("POST", url, **kwargs)


def safe_json(resp: httpx.Response | None) -> dict | list | None:
    """Parse a response body as JSON, returning ``None`` on any failure."""
    if resp is None:
        return None
    try:
        return resp.json()
    except Exception:
        return None


@dataclass
class TokenBundle:
    """The result of an authorization-code exchange or refresh.

    ``expires_in`` is seconds-until-expiry as returned by the provider (``None`` for
    non-expiring tokens, e.g. Mastodon). :meth:`expires_at` converts it to an
    absolute UTC datetime for storage.
    """

    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None
    scopes: str | None = None  # space-delimited granted scopes
    extra: dict = field(default_factory=dict)

    def expires_at(self) -> datetime | None:
        if self.expires_in is None:
            return None
        try:
            return datetime.now(timezone.utc) + timedelta(seconds=int(self.expires_in))
        except (TypeError, ValueError):
            return None


@dataclass
class Identity:
    """The user's identity on the provider (none of these are secrets)."""

    external_id: str
    external_handle: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    extra: dict = field(default_factory=dict)


class OAuthProvider(ABC):
    """Abstract per-platform OAuth adapter.

    Subclasses set ``name``, ``label``, ``scopes`` (space-delimited request scopes),
    and implement the auth-code dance plus an owned-content reader. Every network
    method must degrade to a safe empty/no-op result rather than raising, so a scan
    never breaks because a provider is down or a token expired.
    """

    #: short id used as the URL segment and stored on ``LinkedAccount.provider``
    name: str = "base"
    #: human label for the UI cards
    label: str = "Base"
    #: space-delimited scopes requested at authorize time
    scopes: str = ""

    # --- configuration --------------------------------------------------------
    @abstractmethod
    def is_configured(self) -> bool:
        """Whether global app credentials are present (Mastodon: always True)."""
        raise NotImplementedError

    # --- the authorization-code dance -----------------------------------------
    @abstractmethod
    def build_authorize_url(
        self, *, state: str, redirect_uri: str, **extra
    ) -> str:
        """Build the full provider authorize URL the browser is sent to."""
        raise NotImplementedError

    @abstractmethod
    def exchange_code(
        self, *, code: str, redirect_uri: str, **extra
    ) -> TokenBundle | None:
        """Exchange an auth code for tokens. ``None`` on failure (never raises)."""
        raise NotImplementedError

    def refresh(self, *, refresh_token: str, **extra) -> TokenBundle | None:
        """Refresh an access token. Default: unsupported (returns ``None``)."""
        return None

    @abstractmethod
    def fetch_identity(self, *, access_token: str, **extra) -> Identity | None:
        """Look up the connected account's id/handle/name. ``None`` on failure."""
        raise NotImplementedError

    def revoke(self, *, access_token: str, **extra) -> bool:
        """Best-effort upstream token revocation. Default: no-op (returns True)."""
        return True

    # --- owned-content read ----------------------------------------------------
    @abstractmethod
    def fetch_own_content(
        self, *, access_token: str, limit: int = 25, **extra
    ) -> list[RawMention]:
        """Return the user's OWN posts as ``RawMention`` items.

        ``source`` MUST be ``f"{self.name}_owned"``. Must never raise — return ``[]``
        if the token is bad/expired or the provider is unreachable.
        """
        raise NotImplementedError
