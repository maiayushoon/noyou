"""Threads (Meta) OAuth adapter — reads the user's OWN threads.

Own-account reads (``GET /me/threads``) work with ``threads_basic`` for own/test
users without full App Review. Standard auth-code flow against
``https://threads.net`` / ``https://graph.threads.net``.

Scopes: ``threads_basic``. Requires ``THREADS_APP_ID`` / ``THREADS_APP_SECRET``.
"""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlencode

from ...connectors.base import RawMention
from ...core.config import settings
from .base import Identity, OAuthProvider, TokenBundle, safe_get, safe_json, safe_post

_AUTHORIZE_URL = "https://threads.net/oauth/authorize"
_TOKEN_URL = "https://graph.threads.net/oauth/access_token"
_API = "https://graph.threads.net/v1.0"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


class ThreadsProvider(OAuthProvider):
    name = "threads"
    label = "Threads"
    scopes = "threads_basic"

    def is_configured(self) -> bool:
        return bool(settings.threads_app_id and settings.threads_app_secret)

    def build_authorize_url(self, *, state: str, redirect_uri: str, **extra) -> str:
        params = {
            "client_id": settings.threads_app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scopes,
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(self, *, code: str, redirect_uri: str, **extra) -> TokenBundle | None:
        resp = safe_post(
            _TOKEN_URL,
            data={
                "client_id": settings.threads_app_id,
                "client_secret": settings.threads_app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return TokenBundle(
            access_token=data["access_token"],
            refresh_token=None,
            # Short-lived token; expires_in present on long-lived exchanges only.
            expires_in=data.get("expires_in"),
            scopes=self.scopes,
            extra={"user_id": data.get("user_id")},
        )

    def refresh(self, *, refresh_token: str, **extra) -> TokenBundle | None:
        # Threads refreshes a LONG-LIVED token using the token itself, not a
        # separate refresh token. The token helper passes the current access token.
        access_token = extra.get("access_token") or refresh_token
        if not access_token:
            return None
        resp = safe_get(
            f"{_API}/refresh_access_token",
            params={"grant_type": "th_refresh_token", "access_token": access_token},
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return TokenBundle(
            access_token=data["access_token"],
            refresh_token=None,
            expires_in=data.get("expires_in"),
            scopes=self.scopes,
        )

    def fetch_identity(self, *, access_token: str, **extra) -> Identity | None:
        resp = safe_get(
            f"{_API}/me",
            params={
                "fields": "id,username,name,threads_profile_picture_url",
                "access_token": access_token,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("id"):
            return None
        username = data.get("username")
        return Identity(
            external_id=str(data["id"]),
            external_handle=username,
            display_name=data.get("name") or username,
            avatar_url=data.get("threads_profile_picture_url"),
        )

    def fetch_own_content(
        self, *, access_token: str, limit: int = 25, **extra
    ) -> list[RawMention]:
        resp = safe_get(
            f"{_API}/me/threads",
            params={
                "fields": "id,text,permalink,timestamp,username",
                "limit": max(1, min(limit, 100)),
                "access_token": access_token,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict):
            return []
        out: list[RawMention] = []
        for item in data.get("data") or []:
            if not isinstance(item, dict):
                continue
            tid = item.get("id")
            if not tid:
                continue
            out.append(
                RawMention(
                    source=f"{self.name}_owned",
                    external_id=str(tid),
                    content=item.get("text") or "",
                    url=item.get("permalink"),
                    author=item.get("username"),
                    published_at=_parse_iso(item.get("timestamp")),
                )
            )
        return out
