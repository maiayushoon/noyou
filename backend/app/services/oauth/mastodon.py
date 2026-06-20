"""Mastodon OAuth adapter — the lowest-friction provider.

Mastodon needs NO global app credentials: each instance is an independent server,
so the adapter dynamically registers an app per instance via ``POST /api/v1/apps``
at connect time and caches the returned client creds (keyed by instance URL). It is
therefore ALWAYS configured. Tokens do not expire, so refresh is a no-op.

Scopes are read-only: ``read:accounts read:statuses``.
"""
from __future__ import annotations

import ipaddress
import re
import socket
from datetime import datetime
from urllib.parse import urlencode, urlparse

from ...connectors.base import RawMention
from ...core.config import settings
from .base import Identity, OAuthProvider, TokenBundle, safe_get, safe_json, safe_post

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

# Per-instance client credentials, cached for the process lifetime. Keyed by the
# normalized instance base URL. These are app (not user) creds — not secret tokens.
_INSTANCE_APPS: dict[str, dict] = {}


def _strip_html(value: str | None) -> str:
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


def _normalize_instance(instance_url: str | None) -> str:
    """Return a safe ``scheme://host[:port]`` base, or ``""`` if invalid/unsafe.

    The instance URL is user-supplied and used in outbound requests, so this is an
    SSRF chokepoint. We require https (http only in development), forbid embedded
    credentials, strip any path/query, and — critically — reject hosts that resolve
    to private, loopback, link-local, reserved, or otherwise non-public addresses so
    a user can't point us at cloud metadata (169.254.169.254) or internal services.
    Callers already treat ``""`` as a hard failure.
    """
    if not instance_url:
        return ""
    raw = instance_url.strip()
    if not raw:
        return ""
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    parsed = urlparse(raw)
    scheme = (parsed.scheme or "").lower()
    host = parsed.hostname
    if not host or scheme not in ("http", "https"):
        return ""
    # Plain http is only acceptable for local development.
    if scheme == "http" and settings.environment != "development":
        return ""
    # Reject userinfo (user:pass@host) — a common SSRF/parsing-confusion vector.
    if parsed.username or parsed.password:
        return ""

    # Resolve and reject any non-public address the host maps to.
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if scheme == "https" else 80))
    except Exception:
        return ""
    for info in infos:
        ip_str = info[4][0]
        try:
            addr = ipaddress.ip_address(ip_str)
        except ValueError:
            return ""
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        ):
            return ""

    netloc = host if not parsed.port else f"{host}:{parsed.port}"
    return f"{scheme}://{netloc}"


class MastodonProvider(OAuthProvider):
    name = "mastodon"
    label = "Mastodon"
    scopes = "read:accounts read:statuses"

    def is_configured(self) -> bool:
        # Self-registers per instance — always available.
        return True

    def _register_app(self, instance_base: str, redirect_uri: str) -> dict | None:
        """Dynamically register (or reuse a cached) Mastodon app on the instance."""
        cached = _INSTANCE_APPS.get(instance_base)
        if cached:
            return cached
        resp = safe_post(
            f"{instance_base}/api/v1/apps",
            data={
                "client_name": settings.mastodon_app_name or "NoYou",
                "redirect_uris": redirect_uri,
                "scopes": self.scopes,
                "website": settings.frontend_url,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("client_id"):
            return None
        _INSTANCE_APPS[instance_base] = data
        return data

    def build_authorize_url(self, *, state: str, redirect_uri: str, **extra) -> str:
        instance_base = _normalize_instance(extra.get("instance_url"))
        if not instance_base:
            return ""
        app = self._register_app(instance_base, redirect_uri)
        if not app:
            return ""
        params = {
            "response_type": "code",
            "client_id": app["client_id"],
            "redirect_uri": redirect_uri,
            "scope": self.scopes,
            "state": state,
        }
        return f"{instance_base}/oauth/authorize?{urlencode(params)}"

    def exchange_code(self, *, code: str, redirect_uri: str, **extra) -> TokenBundle | None:
        instance_base = _normalize_instance(extra.get("instance_url"))
        if not instance_base:
            return None
        app = self._register_app(instance_base, redirect_uri)
        if not app:
            return None
        resp = safe_post(
            f"{instance_base}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": app["client_id"],
                "client_secret": app.get("client_secret", ""),
                "redirect_uri": redirect_uri,
                "scope": self.scopes,
            },
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return TokenBundle(
            access_token=data["access_token"],
            refresh_token=None,
            expires_in=None,  # Mastodon tokens do not expire
            scopes=data.get("scope") or self.scopes,
        )

    def fetch_identity(self, *, access_token: str, **extra) -> Identity | None:
        instance_base = _normalize_instance(extra.get("instance_url"))
        if not instance_base:
            return None
        resp = safe_get(
            f"{instance_base}/api/v1/accounts/verify_credentials",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        data = safe_json(resp)
        if not isinstance(data, dict) or not data.get("id"):
            return None
        handle = data.get("acct") or data.get("username")
        return Identity(
            external_id=str(data["id"]),
            external_handle=handle,
            display_name=data.get("display_name") or handle,
            avatar_url=data.get("avatar"),
        )

    def revoke(self, *, access_token: str, **extra) -> bool:
        instance_base = _normalize_instance(extra.get("instance_url"))
        if not instance_base:
            return True
        app = _INSTANCE_APPS.get(instance_base)
        if not app:
            return True
        safe_post(
            f"{instance_base}/oauth/revoke",
            data={
                "client_id": app.get("client_id", ""),
                "client_secret": app.get("client_secret", ""),
                "token": access_token,
            },
        )
        return True

    def fetch_own_content(
        self, *, access_token: str, limit: int = 25, **extra
    ) -> list[RawMention]:
        instance_base = _normalize_instance(extra.get("instance_url"))
        if not instance_base:
            return []
        headers = {"Authorization": f"Bearer {access_token}"}
        identity = self.fetch_identity(access_token=access_token, instance_url=instance_base)
        if identity is None:
            return []
        resp = safe_get(
            f"{instance_base}/api/v1/accounts/{identity.external_id}/statuses",
            headers=headers,
            params={"limit": max(1, min(limit, 40)), "exclude_reblogs": "true"},
        )
        data = safe_json(resp)
        if not isinstance(data, list):
            return []
        out: list[RawMention] = []
        for status in data:
            if not isinstance(status, dict):
                continue
            sid = status.get("id")
            if not sid:
                continue
            out.append(
                RawMention(
                    source=f"{self.name}_owned",
                    external_id=str(sid),
                    content=_strip_html(status.get("content")),
                    url=status.get("url") or status.get("uri"),
                    author=identity.external_handle,
                    published_at=_parse_iso(status.get("created_at")),
                    extra={"instance_url": instance_base},
                )
            )
        return out
