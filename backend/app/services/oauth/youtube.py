"""YouTube (Google) OAuth adapter — reads the user's OWN uploads.

Standard Google OAuth 2.0 auth-code flow with refresh tokens. Owned content is
enumerated as: ``channels.list?mine=true`` -> the channel's uploads playlist ->
``playlistItems.list`` (each item is one of the user's own videos).

Scopes are read-only: ``youtube.readonly openid``. Requires
``GOOGLE_OAUTH_CLIENT_ID`` / ``GOOGLE_OAUTH_CLIENT_SECRET`` (distinct from the
``GOOGLE_API_KEY``/``GOOGLE_CSE_ID`` used by the public search connector).
"""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlencode

from ...connectors.base import RawMention
from ...core.config import settings
from .base import Identity, OAuthProvider, TokenBundle, safe_get, safe_json, safe_post

_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
_API = "https://www.googleapis.com/youtube/v3"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


class YouTubeProvider(OAuthProvider):
    name = "youtube"
    label = "YouTube"
    scopes = "https://www.googleapis.com/auth/youtube.readonly openid"

    def is_configured(self) -> bool:
        return bool(settings.google_oauth_client_id and settings.google_oauth_client_secret)

    def build_authorize_url(self, *, state: str, redirect_uri: str, **extra) -> str:
        params = {
            "response_type": "code",
            "client_id": settings.google_oauth_client_id,
            "redirect_uri": redirect_uri,
            "scope": self.scopes,
            "state": state,
            "access_type": "offline",  # request a refresh token
            "prompt": "consent",
            "include_granted_scopes": "true",
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(self, *, code: str, redirect_uri: str, **extra) -> TokenBundle | None:
        resp = safe_post(
            _TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "redirect_uri": redirect_uri,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return TokenBundle(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            scopes=data.get("scope") or self.scopes,
        )

    def refresh(self, *, refresh_token: str, **extra) -> TokenBundle | None:
        if not refresh_token:
            return None
        resp = safe_post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return TokenBundle(
            access_token=data["access_token"],
            # Google omits refresh_token on refresh; keep the existing one.
            refresh_token=data.get("refresh_token") or refresh_token,
            expires_in=data.get("expires_in"),
            scopes=data.get("scope") or self.scopes,
        )

    def _own_channel(self, access_token: str) -> dict | None:
        resp = safe_get(
            f"{_API}/channels",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"part": "snippet,contentDetails", "mine": "true"},
        )
        data = safe_json(resp)
        if not isinstance(data, dict):
            return None
        items = data.get("items") or []
        if not items or not isinstance(items[0], dict):
            return None
        return items[0]

    def fetch_identity(self, *, access_token: str, **extra) -> Identity | None:
        channel = self._own_channel(access_token)
        if not channel or not channel.get("id"):
            return None
        snippet = channel.get("snippet") or {}
        thumbs = (snippet.get("thumbnails") or {}).get("default") or {}
        return Identity(
            external_id=str(channel["id"]),
            external_handle=snippet.get("customUrl") or snippet.get("title"),
            display_name=snippet.get("title"),
            avatar_url=thumbs.get("url"),
        )

    def revoke(self, *, access_token: str, **extra) -> bool:
        safe_post(_REVOKE_URL, data={"token": access_token})
        return True

    def fetch_own_content(
        self, *, access_token: str, limit: int = 25, **extra
    ) -> list[RawMention]:
        headers = {"Authorization": f"Bearer {access_token}"}
        channel = self._own_channel(access_token)
        if not channel:
            return []
        uploads = (
            (channel.get("contentDetails") or {})
            .get("relatedPlaylists", {})
            .get("uploads")
        )
        if not uploads:
            return []
        channel_title = (channel.get("snippet") or {}).get("title")
        resp = safe_get(
            f"{_API}/playlistItems",
            headers=headers,
            params={
                "part": "snippet,contentDetails",
                "playlistId": uploads,
                "maxResults": max(1, min(limit, 50)),
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict):
            return []
        out: list[RawMention] = []
        for item in data.get("items") or []:
            if not isinstance(item, dict):
                continue
            snippet = item.get("snippet") or {}
            details = item.get("contentDetails") or {}
            video_id = details.get("videoId") or (
                (snippet.get("resourceId") or {}).get("videoId")
            )
            if not video_id:
                continue
            out.append(
                RawMention(
                    source=f"{self.name}_owned",
                    external_id=str(video_id),
                    content=snippet.get("description") or "",
                    title=snippet.get("title"),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    author=channel_title or snippet.get("channelTitle"),
                    published_at=_parse_iso(
                        details.get("videoPublishedAt") or snippet.get("publishedAt")
                    ),
                )
            )
        return out
