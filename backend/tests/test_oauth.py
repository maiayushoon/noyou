"""Unit tests for the OAuth Connections internals (no network, no HTTP client).

Covers the security-critical pure functions behind account linking:
  * token encryption round-trips and fails safe on garbage,
  * the HMAC-signed ``state`` token (create/verify + tamper/expiry/typ rejection),
  * the provider registry (the five wired providers and their config gating),
  * Mastodon's ``_normalize_instance`` SSRF chokepoint, and
  * PKCE: the ``create_pkce_pair`` shape plus reddit/youtube authorize-URL building.

Everything here is hermetic: PKCE/state/crypto are local computation, and the only
provider methods exercised (``build_authorize_url``) build a string without any
network call. ``_normalize_instance`` is tested directly with ``getaddrinfo`` stubbed
so no DNS lookup happens.
"""
from __future__ import annotations

import socket
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.crypto import decrypt_token, encrypt_token
from app.core.database import SessionLocal
from app.core.security import (
    _OAUTH_STATE_TYP,
    create_state_token,
    verify_state_token,
)
from app.services.oauth import get_provider, list_providers
from app.services.oauth.base import OAuthProvider
from app.services.oauth.mastodon import _normalize_instance


# --- crypto round-trip -------------------------------------------------------
def test_encrypt_decrypt_round_trip():
    token = "ya29.super-secret-access-token-value"
    ciphertext = encrypt_token(token)
    assert ciphertext != token  # actually encrypted, not stored in the clear
    assert decrypt_token(ciphertext) == token


def test_encrypt_empty_round_trips_to_empty():
    assert decrypt_token(encrypt_token("")) == ""


def test_decrypt_garbage_returns_empty_not_raises():
    # Unparseable / wrong-key ciphertext must degrade to "" rather than raising,
    # so a rotated SECRET_KEY makes accounts re-link instead of 500ing a scan.
    assert decrypt_token("not-a-fernet-token") == ""
    assert decrypt_token("") == ""
    assert decrypt_token("!!!@@@###") == ""


# --- OAuth state token (CSRF / PKCE carrier) ---------------------------------
def test_state_token_round_trip_preserves_payload():
    token = create_state_token({"uid": "u1", "provider": "reddit", "code_verifier": "v"})
    payload = verify_state_token(token)
    assert payload is not None
    assert payload["uid"] == "u1"
    assert payload["provider"] == "reddit"
    assert payload["code_verifier"] == "v"
    assert payload["typ"] == _OAUTH_STATE_TYP
    assert payload["nonce"]  # a CSRF nonce is always added


def test_state_token_tampered_is_rejected():
    token = create_state_token({"uid": "u1", "provider": "reddit"})
    # Flip a character in the signature segment -> signature verification fails.
    head, body, sig = token.split(".")
    bad_sig = ("A" if sig[0] != "A" else "B") + sig[1:]
    assert verify_state_token(f"{head}.{body}.{bad_sig}") is None


def test_state_token_expired_is_rejected():
    token = create_state_token({"uid": "u1", "provider": "reddit"}, ttl_seconds=-10)
    assert verify_state_token(token) is None


def test_state_token_wrong_typ_is_rejected():
    # A correctly-signed JWT that is NOT an oauth_state token must not pass — this
    # defeats cross-token confusion (e.g. replaying an access token as state).
    now = datetime.now(timezone.utc)
    forged = jwt.encode(
        {
            "uid": "u1",
            "provider": "reddit",
            "typ": "access",
            "iat": now,
            "exp": now + timedelta(seconds=600),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    assert verify_state_token(forged) is None


def test_state_token_wrong_secret_is_rejected():
    now = datetime.now(timezone.utc)
    forged = jwt.encode(
        {"typ": _OAUTH_STATE_TYP, "iat": now, "exp": now + timedelta(seconds=600)},
        "the-wrong-secret",
        algorithm=settings.algorithm,
    )
    assert verify_state_token(forged) is None


# --- provider registry -------------------------------------------------------
def test_registry_has_the_five_wired_providers():
    names = {p.name for p in list_providers()}
    assert names == {"mastodon", "youtube", "reddit", "threads", "instagram"}


def test_get_provider_is_case_insensitive_and_safe():
    assert get_provider("REDDIT").name == "reddit"
    assert get_provider("  youtube  ").name == "youtube"
    assert get_provider("nope") is None
    assert get_provider("") is None
    assert get_provider(None) is None


def test_mastodon_is_always_configured():
    # Mastodon self-registers per instance, so it never needs global app creds.
    assert get_provider("mastodon").is_configured() is True


def test_keyed_providers_are_gated_when_unconfigured():
    # The test env supplies no OAuth app credentials, so every keyed provider must
    # report itself unconfigured (the connect endpoint 400s on these).
    for name in ("youtube", "reddit", "threads", "instagram"):
        assert get_provider(name).is_configured() is False


def test_keyed_provider_configured_when_creds_present(monkeypatch):
    monkeypatch.setattr(settings, "reddit_oauth_client_id", "id", raising=False)
    monkeypatch.setattr(settings, "reddit_oauth_client_secret", "secret", raising=False)
    assert get_provider("reddit").is_configured() is True


# --- pkce/self-refresh provider flags ----------------------------------------
def test_pkce_and_self_refresh_flags():
    assert get_provider("reddit").uses_pkce is True
    assert get_provider("youtube").uses_pkce is True
    # Mastodon stays a non-PKCE flow.
    assert get_provider("mastodon").uses_pkce is False
    # Meta providers self-refresh with the access token (no stored refresh token).
    assert get_provider("instagram").refreshes_with_access_token is True
    assert get_provider("threads").refreshes_with_access_token is True
    assert get_provider("reddit").refreshes_with_access_token is False


# --- Mastodon instance SSRF chokepoint ---------------------------------------
def _stub_resolves_to(monkeypatch, ip: str) -> None:
    """Force ``getaddrinfo`` to resolve any host to ``ip`` (no real DNS)."""

    def fake_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port or 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1",       # loopback (literal)
        "https://localhost",       # loopback (name -> resolved below)
        "https://10.0.0.5",        # private
        "https://192.168.1.10",    # private
        "https://169.254.169.254", # link-local (cloud metadata)
        "https://[::1]",           # IPv6 loopback
        "https://user:pass@mastodon.social",  # embedded credentials
        "",                        # empty
        None,                      # missing
    ],
)
def test_normalize_instance_rejects_unsafe(url, monkeypatch):
    # Even if a name resolved to something public, the literal-IP cases are unsafe;
    # for the name cases we resolve to a loopback IP to exercise the IP guard.
    _stub_resolves_to(monkeypatch, "127.0.0.1")
    assert _normalize_instance(url) == ""


def test_normalize_instance_rejects_http_in_production(monkeypatch):
    _stub_resolves_to(monkeypatch, "93.184.216.34")  # public
    monkeypatch.setattr(settings, "environment", "production", raising=False)
    # Plain http to an otherwise-public host is rejected outside development.
    assert _normalize_instance("http://mastodon.social") == ""


def test_normalize_instance_accepts_public_https(monkeypatch):
    _stub_resolves_to(monkeypatch, "93.184.216.34")  # a public address
    monkeypatch.setattr(settings, "environment", "production", raising=False)
    assert _normalize_instance("https://mastodon.social") == "https://mastodon.social"
    # A bare host gets https:// prepended; path/query are stripped.
    assert _normalize_instance("mastodon.social/foo?x=1") == "https://mastodon.social"


# --- PKCE pair + authorize-URL shapes ----------------------------------------
def test_create_pkce_pair_shape():
    import base64
    import hashlib

    verifier, challenge = OAuthProvider.create_pkce_pair()
    # High-entropy verifier; base64url(no-pad) challenge.
    assert len(verifier) >= 43
    assert "=" not in challenge  # padding stripped
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    assert challenge == expected
    # Distinct each call (it draws fresh randomness).
    assert OAuthProvider.create_pkce_pair()[0] != verifier


def test_reddit_authorize_url_includes_pkce_when_challenge_supplied():
    reddit = get_provider("reddit")
    url = reddit.build_authorize_url(
        state="STATE", redirect_uri="https://backend/cb", code_challenge="CHAL"
    )
    assert url.startswith("https://www.reddit.com/api/v1/authorize?")
    assert "state=STATE" in url
    assert "response_type=code" in url
    assert "duration=permanent" in url  # still requests a refresh token
    assert "code_challenge=CHAL" in url
    assert "code_challenge_method=S256" in url


def test_reddit_authorize_url_omits_pkce_without_challenge():
    url = get_provider("reddit").build_authorize_url(
        state="STATE", redirect_uri="https://backend/cb"
    )
    assert "code_challenge" not in url


def test_youtube_authorize_url_includes_pkce_when_challenge_supplied():
    youtube = get_provider("youtube")
    url = youtube.build_authorize_url(
        state="STATE", redirect_uri="https://backend/cb", code_challenge="CHAL"
    )
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "access_type=offline" in url  # still requests a refresh token
    assert "code_challenge=CHAL" in url
    assert "code_challenge_method=S256" in url


def test_youtube_authorize_url_omits_pkce_without_challenge():
    url = get_provider("youtube").build_authorize_url(
        state="STATE", redirect_uri="https://backend/cb"
    )
    assert "code_challenge" not in url


# --- self-refresh in get_valid_token -----------------------------------------
# These exercise the token helper directly against the DB (the autouse ``fresh_db``
# fixture from conftest gives each test a clean schema). Provider ``refresh`` is
# stubbed so no network call happens.
def _expired_dt():
    return datetime.now(timezone.utc) - timedelta(hours=1)


def _make_account(db, provider, *, access="acc", refresh_enc=None, expires=None):
    from app.core.crypto import encrypt_token
    from app.models.linked_account import LinkedAccount
    from app.models.user import User

    user = User(
        email=f"tok-{provider}@test.com", full_name="T", password_hash="x", plan="pro"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    linked = LinkedAccount(
        user_id=user.id,
        provider=provider,
        external_id="ext1",
        status="connected",
        access_token_enc=encrypt_token(access) if access is not None else "garbage-cipher",
        refresh_token_enc=refresh_enc,
        token_expires_at=expires,
    )
    db.add(linked)
    db.commit()
    db.refresh(linked)
    return linked


def test_self_refresh_provider_refreshes_with_access_token(monkeypatch):
    # Instagram has NO stored refresh token; an expired-but-decryptable access token
    # must trigger a self-refresh (using the access token itself) instead of expiring.
    from app.services.oauth import get_provider as _gp
    from app.services.oauth import tokens as tokmod
    from app.services.oauth.base import TokenBundle

    db = SessionLocal()
    try:
        linked = _make_account(db, "instagram", access="old-ig", expires=_expired_dt())

        captured = {}

        def fake_refresh(self, *, refresh_token, **extra):
            captured["refresh_token"] = refresh_token
            captured["access_token"] = extra.get("access_token")
            return TokenBundle(access_token="new-ig", refresh_token=None, expires_in=3600)

        monkeypatch.setattr(type(_gp("instagram")), "refresh", fake_refresh)

        token = tokmod.get_valid_token(db, linked)
        assert token == "new-ig"
        # The current access token was passed as the refresh credential.
        assert captured["refresh_token"] == "old-ig"
        assert captured["access_token"] == "old-ig"
        # Persisted: new ciphertext + connected status + fresh expiry.
        db.refresh(linked)
        assert linked.status == "connected"
        assert decrypt_token(linked.access_token_enc) == "new-ig"
    finally:
        db.close()


def test_self_refresh_skipped_when_token_unreadable(monkeypatch):
    # If the stored access token can't be decrypted, even a self-refresh provider
    # has nothing to refresh WITH — it must expire, not call refresh.
    from app.services.oauth import get_provider as _gp
    from app.services.oauth import tokens as tokmod

    db = SessionLocal()
    try:
        linked = _make_account(db, "instagram", access=None, expires=_expired_dt())

        def boom(self, **kwargs):  # pragma: no cover - must never be called
            raise AssertionError("refresh should not be attempted on an unreadable token")

        monkeypatch.setattr(type(_gp("instagram")), "refresh", boom)

        try:
            tokmod.get_valid_token(db, linked)
            raise AssertionError("expected TokenExpired")
        except tokmod.TokenExpired:
            pass
        db.refresh(linked)
        assert linked.status == "expired"
    finally:
        db.close()


def test_non_self_refresh_provider_without_refresh_token_expires(monkeypatch):
    # Reddit uses a real refresh token. With none stored and an expired access token,
    # it must expire (NOT fall through to a self-refresh).
    from app.services.oauth import get_provider as _gp
    from app.services.oauth import tokens as tokmod

    db = SessionLocal()
    try:
        linked = _make_account(db, "reddit", access="acc", expires=_expired_dt())

        def boom(self, **kwargs):  # pragma: no cover - must never be called
            raise AssertionError("reddit must not self-refresh")

        monkeypatch.setattr(type(_gp("reddit")), "refresh", boom)

        try:
            tokmod.get_valid_token(db, linked)
            raise AssertionError("expected TokenExpired")
        except tokmod.TokenExpired:
            pass
        db.refresh(linked)
        assert linked.status == "expired"
    finally:
        db.close()


def test_real_refresh_token_provider_refreshes(monkeypatch):
    # Reddit WITH a stored refresh token refreshes normally.
    from app.core.crypto import encrypt_token
    from app.services.oauth import get_provider as _gp
    from app.services.oauth import tokens as tokmod
    from app.services.oauth.base import TokenBundle

    db = SessionLocal()
    try:
        linked = _make_account(
            db,
            "reddit",
            access="old",
            refresh_enc=encrypt_token("refresh-tok"),
            expires=_expired_dt(),
        )

        captured = {}

        def fake_refresh(self, *, refresh_token, **extra):
            captured["refresh_token"] = refresh_token
            return TokenBundle(
                access_token="new-acc", refresh_token="refresh-tok2", expires_in=3600
            )

        monkeypatch.setattr(type(_gp("reddit")), "refresh", fake_refresh)

        token = tokmod.get_valid_token(db, linked)
        assert token == "new-acc"
        assert captured["refresh_token"] == "refresh-tok"  # the stored refresh token
    finally:
        db.close()


def test_unexpired_token_returned_without_refresh(monkeypatch):
    # A still-valid token is returned as-is with no provider call.
    from app.services.oauth import get_provider as _gp
    from app.services.oauth import tokens as tokmod

    db = SessionLocal()
    try:
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        linked = _make_account(db, "reddit", access="still-good", expires=future)

        def boom(self, **kwargs):  # pragma: no cover - must never be called
            raise AssertionError("no refresh for an unexpired token")

        monkeypatch.setattr(type(_gp("reddit")), "refresh", boom)
        assert tokmod.get_valid_token(db, linked) == "still-good"
    finally:
        db.close()
