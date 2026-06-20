"""Reddit OAuth adapter — reads the user's OWN submissions and comments.

Standard OAuth 2.0 auth-code flow with permanent refresh tokens
(``duration=permanent``). Owned content is read from
``/user/{handle}/submitted`` and ``/user/{handle}/comments`` against the
authenticated ``oauth.reddit.com`` host.

Scopes: ``identity history read``. Requires ``REDDIT_OAUTH_CLIENT_ID`` /
``REDDIT_OAUTH_CLIENT_SECRET`` (a 'web app' client, distinct from the
client-credentials ``REDDIT_CLIENT_ID``/``SECRET`` used by the public search
connector). Reuses ``REDDIT_USER_AGENT`` for the required header.
"""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx

from ...connectors.base import RawMention
from ...core.config import settings
from .base import Identity, OAuthProvider, TokenBundle, safe_get, safe_json, safe_post

_AUTHORIZE_URL = "https://www.reddit.com/api/v1/authorize"
_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_REVOKE_URL = "https://www.reddit.com/api/v1/revoke_token"
_API = "https://oauth.reddit.com"


def _parse_epoch(value) -> datetime | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError):
        return None


class RedditProvider(OAuthProvider):
    name = "reddit"
    label = "Reddit"
    scopes = "identity history read"
    uses_pkce = True

    def is_configured(self) -> bool:
        return bool(settings.reddit_oauth_client_id and settings.reddit_oauth_client_secret)

    def _user_agent(self) -> str:
        return settings.reddit_user_agent or "noyou/1.0"

    def _auth(self) -> httpx.BasicAuth:
        # Reddit requires HTTP Basic auth (client_id:client_secret) on token calls.
        return httpx.BasicAuth(
            settings.reddit_oauth_client_id, settings.reddit_oauth_client_secret
        )

    def build_authorize_url(self, *, state: str, redirect_uri: str, **extra) -> str:
        params = {
            "client_id": settings.reddit_oauth_client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": redirect_uri,
            "duration": "permanent",  # request a refresh token
            "scope": self.scopes,
        }
        # PKCE (S256): bind this authorize request to the verifier in the signed state.
        code_challenge = extra.get("code_challenge")
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(self, *, code: str, redirect_uri: str, **extra) -> TokenBundle | None:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        # PKCE: prove possession of the verifier that produced the authorize challenge.
        code_verifier = extra.get("code_verifier")
        if code_verifier:
            data["code_verifier"] = code_verifier
        resp = safe_post(
            _TOKEN_URL,
            data=data,
            auth=self._auth(),
            headers={"User-Agent": self._user_agent()},
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
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            auth=self._auth(),
            headers={"User-Agent": self._user_agent()},
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return TokenBundle(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token") or refresh_token,
            expires_in=data.get("expires_in"),
            scopes=data.get("scope") or self.scopes,
        )

    def fetch_identity(self, *, access_token: str, **extra) -> Identity | None:
        resp = safe_get(
            f"{_API}/api/v1/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self._user_agent(),
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("id"):
            return None
        name = data.get("name")
        return Identity(
            external_id=str(data["id"]),
            external_handle=name,
            display_name=name,
            avatar_url=(data.get("icon_img") or "").split("?")[0] or None,
        )

    def revoke(self, *, access_token: str, **extra) -> bool:
        safe_post(
            _REVOKE_URL,
            data={"token": access_token, "token_type_hint": "access_token"},
            auth=self._auth(),
            headers={"User-Agent": self._user_agent()},
        )
        return True

    def _fetch_listing(self, path: str, access_token: str, handle: str, limit: int) -> list[dict]:
        resp = safe_get(
            f"{_API}/user/{handle}/{path}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self._user_agent(),
            },
            params={"limit": max(1, min(limit, 100))},
        )
        data = safe_json(resp)
        if not isinstance(data, dict):
            return []
        return (data.get("data") or {}).get("children") or []

    def fetch_own_content(
        self, *, access_token: str, limit: int = 25, **extra
    ) -> list[RawMention]:
        handle = extra.get("external_handle")
        if not handle:
            identity = self.fetch_identity(access_token=access_token)
            if identity is None:
                return []
            handle = identity.external_handle
        if not handle:
            return []

        out: list[RawMention] = []
        for path in ("submitted", "comments"):
            for child in self._fetch_listing(path, access_token, handle, limit):
                if not isinstance(child, dict):
                    continue
                d = child.get("data") or {}
                fullname = d.get("name")  # t3_/t1_ globally-unique fullname
                if not fullname:
                    continue
                permalink = d.get("permalink") or ""
                out.append(
                    RawMention(
                        source=f"{self.name}_owned",
                        external_id=str(fullname),
                        content=d.get("selftext") or d.get("body") or d.get("title") or "",
                        title=d.get("title"),
                        url=("https://reddit.com" + permalink) if permalink else d.get("url"),
                        author=handle,
                        published_at=_parse_epoch(d.get("created_utc")),
                        extra={"subreddit": d.get("subreddit")},
                    )
                )
        return out
