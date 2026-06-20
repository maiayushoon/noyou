"""Account-linking (OAuth) endpoints — connect/disconnect the user's own accounts.

These routes let a paying user authorize NoYou to read their OWN content on a
platform (YouTube, Reddit, Mastodon, Threads, Instagram, X, ...), so the scanner
can surface their first-party posts alongside third-party mentions. They are the
public face of the OAuth machinery that lives in :mod:`app.services.oauth`.

Security model (see the architect design — ``oauthFlow`` / ``security``):
  * Every endpoint is gated by ``require_plan("pro", "premium", "enterprise")``
    EXCEPT the OAuth ``callback`` — the provider redirect carries no JWT bearer,
    so the callback authenticates via the HMAC-signed ``state`` token instead
    (``create_state_token`` / ``verify_state_token``), which binds the user id,
    provider, a CSRF nonce, and (when used) the PKCE verifier.
  * Tokens are encrypted at rest (``encrypt_token``) and NEVER serialized out of
    the API (the ``ConnectionOut`` schema excludes the ``*_enc`` columns).
  * The callback NEVER 500s — any failure 302s the browser back to the frontend
    with an ``?error=`` query param so the user gets a clean message.
"""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.crypto import decrypt_token, encrypt_token
from ...core.database import get_db
from ...core.plans import require_plan
from ...core.security import create_state_token, verify_state_token
from ...models.linked_account import LinkedAccount
from ...models.user import User
from ...schemas.connection import ConnectionOut, ConnectStartOut, ProviderInfo
from ...services.oauth import get_provider, list_providers
from ..deps import get_current_user

logger = logging.getLogger("noyou.connections")

router = APIRouter(prefix="/connections", tags=["connections"])

# Paid-tier gate shared by every endpoint except the OAuth callback (which is
# authenticated by the signed state token, not a bearer JWT).
_require_paid = require_plan("pro", "premium", "enterprise")


def _callback_redirect_uri(provider: str, request: Request) -> str:
    """The backend-hosted redirect URI registered with each OAuth provider.

    Built from THIS backend's origin (where the callback handler lives), NOT the
    frontend — they are different hosts. ``OAUTH_CALLBACK_BASE_URL`` overrides the
    auto-detected origin for deployments behind a reverse proxy. Tokens are
    exchanged + stored here, then the browser is 302'd back to the frontend
    ``/connections`` page.
    """
    base = (settings.oauth_callback_base_url or "").rstrip("/") or str(
        request.base_url
    ).rstrip("/")
    return f"{base}{settings.api_v1_prefix}/connections/{provider}/callback"


def _frontend_return(*, connected: str | None = None, error: str | None = None) -> RedirectResponse:
    """302 the browser back to the frontend connections page with a status param."""
    base = f"{settings.frontend_url}/connections"
    if connected:
        return RedirectResponse(url=f"{base}?connected={connected}", status_code=302)
    return RedirectResponse(url=f"{base}?error={error or 'unknown'}", status_code=302)


@router.get("", response_model=list[ConnectionOut])
def list_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_paid),
):
    """Return the current user's linked accounts (never any token material)."""
    return db.scalars(
        select(LinkedAccount)
        .where(LinkedAccount.user_id == current_user.id)
        .order_by(LinkedAccount.created_at.desc())
    ).all()


@router.get("/providers", response_model=list[ProviderInfo])
def list_connection_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_paid),
):
    """List every supported provider, marking which are configured + connected.

    Drives the UI's provider cards: ``configured`` reflects whether the server has
    OAuth credentials for the provider, ``connected`` whether THIS user already has
    a non-revoked LinkedAccount for it, and ``scopes_requested`` the read scopes the
    consent screen will ask for (transparency).
    """
    connected_providers = set(
        db.scalars(
            select(LinkedAccount.provider).where(
                LinkedAccount.user_id == current_user.id,
                LinkedAccount.status == "connected",
            )
        ).all()
    )

    infos: list[ProviderInfo] = []
    for provider in list_providers():
        # ``scopes`` is a space-delimited string on the adapter; expose it as a list.
        raw_scopes = getattr(provider, "scopes", "") or ""
        scopes_list = raw_scopes.split() if isinstance(raw_scopes, str) else list(raw_scopes)
        infos.append(
            ProviderInfo(
                provider=provider.name,
                label=provider.label,
                configured=provider.is_configured(),
                connected=provider.name in connected_providers,
                scopes_requested=scopes_list,
            )
        )
    return infos


@router.post("/{provider}/connect", response_model=ConnectStartOut)
def start_connection(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_paid),
    body: dict | None = Body(default=None),
):
    """Begin an OAuth flow — return the provider ``authorize_url`` to redirect to.

    Builds a signed ``state`` token embedding the user id, provider, a PKCE verifier
    (when the provider supports it), and an optional ``instance_url`` (Mastodon).
    The provider adapter assembles the authorize URL with our backend-hosted
    ``redirect_uri``, the requested read scopes, and (for PKCE) the code challenge.
    """
    adapter = get_provider(provider)
    if adapter is None:
        raise HTTPException(status_code=404, detail="Unknown provider")
    if not adapter.is_configured():
        raise HTTPException(
            status_code=400,
            detail=f"{adapter.label} is not configured on this server",
        )

    body = body or {}
    instance_url = (body.get("instance_url") or "").strip() or None

    # PKCE: when an adapter opts in (``uses_pkce``), it generates a verifier/challenge
    # pair; the verifier is carried inside the signed state so the callback completes
    # with no server-side session store. Adapters that don't use PKCE are unaffected.
    code_verifier: str | None = None
    extra: dict = {}
    if getattr(adapter, "uses_pkce", False) and hasattr(adapter, "create_pkce_pair"):
        try:
            code_verifier, code_challenge = adapter.create_pkce_pair()
            extra["code_challenge"] = code_challenge
        except Exception:
            code_verifier = None  # degrade to a non-PKCE flow rather than 500

    state_payload = {
        "uid": current_user.id,
        "provider": adapter.name,
    }
    if code_verifier:
        state_payload["code_verifier"] = code_verifier
    if instance_url:
        state_payload["instance_url"] = instance_url

    state = create_state_token(state_payload)
    redirect_uri = _callback_redirect_uri(adapter.name, request)

    authorize_url = adapter.build_authorize_url(
        state=state,
        redirect_uri=redirect_uri,
        instance_url=instance_url,
        **extra,
    )
    if not authorize_url:
        # e.g. Mastodon per-instance app registration failed, or a bad instance_url.
        raise HTTPException(
            status_code=400,
            detail="Could not start the connection. Check the instance URL and try again.",
        )
    return ConnectStartOut(authorize_url=authorize_url)


@router.get("/{provider}/callback")
def oauth_callback(
    provider: str,
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    """OAuth redirect target — exchange the code, store the connection, return home.

    NOT plan-gated and NOT bearer-authenticated: the provider redirect carries no
    JWT, so trust comes entirely from the signed ``state`` token. This handler NEVER
    raises a 500 to the browser — every failure path 302s back to the frontend with
    an ``?error=`` param so the user sees a clean message instead of a stack trace.
    """
    # Provider-reported errors (user denied consent, etc.) short-circuit.
    if error:
        return _frontend_return(error="denied")
    if not code or not state:
        return _frontend_return(error="invalid_request")

    # 1) Verify + decode the signed state (rejects expired/tampered/wrong-typ).
    payload = verify_state_token(state)
    if not payload:
        return _frontend_return(error="invalid_state")
    if payload.get("provider") != provider:
        return _frontend_return(error="invalid_state")

    user_id = payload.get("uid")
    if not user_id:
        return _frontend_return(error="invalid_state")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        return _frontend_return(error="invalid_state")

    adapter = get_provider(provider)
    if adapter is None:
        return _frontend_return(error="unknown_provider")

    code_verifier = payload.get("code_verifier")
    instance_url = payload.get("instance_url")
    redirect_uri = _callback_redirect_uri(provider, request)

    try:
        # 2) Exchange the authorization code for tokens.
        bundle = adapter.exchange_code(
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            instance_url=instance_url,
        )
        if bundle is None or not getattr(bundle, "access_token", None):
            return _frontend_return(error="exchange_failed")

        # 3) Resolve the user's identity on the provider (external_id/handle).
        identity = adapter.fetch_identity(
            access_token=bundle.access_token,
            instance_url=instance_url,
        )
        if identity is None or not getattr(identity, "external_id", None):
            return _frontend_return(error="identity_failed")

        # 4) Encrypt tokens and upsert the LinkedAccount on (uid, provider, ext_id).
        _upsert_linked_account(
            db,
            user=user,
            provider=provider,
            bundle=bundle,
            identity=identity,
            instance_url=instance_url,
        )
    except Exception:
        # Never leak token material; log only non-secret context.
        logger.exception(
            "oauth callback failed for provider=%s user=%s", provider, user_id
        )
        db.rollback()
        return _frontend_return(error="connect_failed")

    return _frontend_return(connected=provider)


def _upsert_linked_account(
    db: Session,
    *,
    user: User,
    provider: str,
    bundle,
    identity,
    instance_url: str | None,
) -> LinkedAccount:
    """Create or update the user's LinkedAccount for this provider identity.

    Tokens are encrypted before they touch the row. Uniqueness is
    (user_id, provider, external_id) so re-linking the same account updates in place.
    """
    # TokenBundle provides absolute-expiry + space-delimited scopes directly.
    expires_at = bundle.expires_at() if hasattr(bundle, "expires_at") else None
    scopes = getattr(bundle, "scopes", None)
    if isinstance(scopes, (list, tuple, set)):
        scopes = " ".join(str(s) for s in scopes)

    refresh_token = getattr(bundle, "refresh_token", None)

    existing = db.scalar(
        select(LinkedAccount).where(
            LinkedAccount.user_id == user.id,
            LinkedAccount.provider == provider,
            LinkedAccount.external_id == identity.external_id,
        )
    )

    if existing is None:
        existing = LinkedAccount(
            user_id=user.id,
            provider=provider,
            external_id=identity.external_id,
        )
        db.add(existing)

    existing.status = "connected"
    existing.external_handle = getattr(identity, "external_handle", None)
    existing.display_name = getattr(identity, "display_name", None)
    existing.avatar_url = getattr(identity, "avatar_url", None)
    existing.instance_url = instance_url
    existing.access_token_enc = encrypt_token(bundle.access_token)
    existing.refresh_token_enc = encrypt_token(refresh_token) if refresh_token else None
    existing.token_expires_at = expires_at
    existing.scopes = scopes
    existing.last_error = None

    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{linked_id}", status_code=204)
def disconnect(
    linked_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_paid),
):
    """Disconnect (and best-effort upstream-revoke) a linked account.

    Ownership-checked (404 if the row isn't the caller's). We attempt to revoke the
    token upstream so access is killed at the provider, then delete the local row.
    A revoke failure still removes the local connection.
    """
    # Validate the id shape before hitting the DB: a non-UUID path param is a clean
    # 404 on SQLite but raises DataError (500) on a Postgres UUID column.
    try:
        uuid.UUID(str(linked_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Connection not found")

    linked = db.get(LinkedAccount, linked_id)
    if not linked or linked.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Best-effort upstream revocation — never let it block local deletion.
    adapter = get_provider(linked.provider)
    if adapter is not None:
        try:
            access_token = decrypt_token(linked.access_token_enc)
            if access_token:
                adapter.revoke(access_token=access_token, instance_url=linked.instance_url)
        except Exception:
            logger.warning(
                "upstream revoke failed for provider=%s linked=%s user=%s",
                linked.provider, linked.id, current_user.id,
            )

    db.delete(linked)
    db.commit()
