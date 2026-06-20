"""Instagram (Meta) OAuth adapter — reads the user's OWN media.

Reading a user's OWN professional (Business/Creator) account via Instagram Login
needs only Standard Access (no App Review). Owned content comes from
``GET /me/media``; currently-live stories from ``GET /{ig-user-id}/stories``.

Scopes: ``instagram_business_basic``. Requires ``INSTAGRAM_APP_ID`` /
``INSTAGRAM_APP_SECRET``. End users must have a Professional IG account.
"""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlencode

from ...connectors.base import RawMention
from ...core.config import settings
from .base import Identity, OAuthProvider, TokenBundle, safe_get, safe_json, safe_post

_AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
_API = "https://graph.instagram.com"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


class InstagramProvider(OAuthProvider):
    name = "instagram"
    label = "Instagram"
    scopes = "instagram_business_basic"
    # No separate refresh token: long-lived tokens are refreshed using the token itself.
    refreshes_with_access_token = True

    def is_configured(self) -> bool:
        return bool(settings.instagram_app_id and settings.instagram_app_secret)

    def build_authorize_url(self, *, state: str, redirect_uri: str, **extra) -> str:
        params = {
            "client_id": settings.instagram_app_id,
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
                "client_id": settings.instagram_app_id,
                "client_secret": settings.instagram_app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        # Exchange the short-lived token for a long-lived (60-day) one.
        access_token = data["access_token"]
        expires_in = None
        long_resp = safe_get(
            f"{_API}/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": settings.instagram_app_secret,
                "access_token": access_token,
            },
        )
        long_data = safe_json(long_resp)
        if isinstance(long_data, dict) and long_data.get("access_token"):
            access_token = long_data["access_token"]
            expires_in = long_data.get("expires_in")
        return TokenBundle(
            access_token=access_token,
            refresh_token=None,
            expires_in=expires_in,
            scopes=self.scopes,
            extra={"user_id": data.get("user_id")},
        )

    def refresh(self, *, refresh_token: str, **extra) -> TokenBundle | None:
        # IG long-lived tokens are refreshed using the token itself.
        access_token = extra.get("access_token") or refresh_token
        if not access_token:
            return None
        resp = safe_get(
            f"{_API}/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": access_token},
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
                "fields": "id,username,account_type,profile_picture_url",
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
            display_name=username,
            avatar_url=data.get("profile_picture_url"),
        )

    def fetch_own_content(
        self, *, access_token: str, limit: int = 25, **extra
    ) -> list[RawMention]:
        out: list[RawMention] = []
        media_resp = safe_get(
            f"{_API}/me/media",
            params={
                "fields": "id,caption,permalink,timestamp,media_type,username",
                "limit": max(1, min(limit, 100)),
                "access_token": access_token,
            },
        )
        media = safe_json(media_resp)
        if isinstance(media, dict):
            for item in media.get("data") or []:
                if not isinstance(item, dict):
                    continue
                mid = item.get("id")
                if not mid:
                    continue
                out.append(
                    RawMention(
                        source=f"{self.name}_owned",
                        external_id=str(mid),
                        content=item.get("caption") or "",
                        url=item.get("permalink"),
                        author=item.get("username"),
                        published_at=_parse_iso(item.get("timestamp")),
                        extra={"media_type": item.get("media_type")},
                    )
                )

        # Currently-live stories (best-effort; needs the IG user id).
        ig_user_id = extra.get("external_id")
        if ig_user_id:
            stories_resp = safe_get(
                f"{_API}/{ig_user_id}/stories",
                params={
                    "fields": "id,caption,permalink,timestamp,media_type",
                    "access_token": access_token,
                },
            )
            stories = safe_json(stories_resp)
            if isinstance(stories, dict):
                for item in stories.get("data") or []:
                    if not isinstance(item, dict):
                        continue
                    sid = item.get("id")
                    if not sid:
                        continue
                    out.append(
                        RawMention(
                            source=f"{self.name}_owned",
                            external_id=str(sid),
                            content=item.get("caption") or "",
                            url=item.get("permalink"),
                            published_at=_parse_iso(item.get("timestamp")),
                            extra={"media_type": item.get("media_type"), "story": True},
                        )
                    )
        return out
