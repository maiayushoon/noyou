"""Owned-content connector — pulls the user's OWN posts from linked accounts.

Unlike every other connector (Google, Reddit, ...), which is *stateless* and
searches for a keyword, this one is **user-scoped**: it reads the authenticated
user's own feeds via their :class:`~app.models.linked_account.LinkedAccount` rows
(YouTube uploads, Reddit submissions/comments, Mastodon statuses, Threads/Instagram
posts). It still implements the plain ``BaseConnector.search`` contract, so the scan
pipeline treats it identically — dedupe by ``external_id``, analyze, score — with no
downstream changes.

Because it is user-scoped it is instantiated PER USER inside
``scanning._connectors_for(db, user)`` as ``OwnedContentConnector(db, user)`` rather
than via the stateless connector registry.

Key behaviors (per the architect ``connectorDesign``):
  * ``search`` IGNORES the ``query`` argument — there is no keyword, it reads the
    user's own content. It emits all owned mentions on the FIRST call of a scan and
    ``[]`` on every subsequent call (the pipeline calls each connector once per
    query term), guarded by an internal ``_emitted`` flag so we fetch only once.
  * Tokens are obtained through ``get_valid_token`` (centralized refresh). A
    ``TokenExpired`` for one account marks that ``LinkedAccount`` ``expired`` and is
    skipped; OTHER connected accounts still sync.
  * Each synced account is stamped with ``last_synced_at``.
  * It NEVER raises — any per-account failure degrades to no rows for that account,
    mirroring ``connectors/free_web.py`` ``_safe_get`` semantics.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.linked_account import LinkedAccount
from ..models.user import User
from ..services.oauth import get_provider
from ..services.oauth.tokens import TokenExpired, get_valid_token
from .base import BaseConnector, RawMention

logger = logging.getLogger("noyou.connectors.owned")


class OwnedContentConnector(BaseConnector):
    """Emit RawMentions from every connected account the user owns."""

    name = "owned"
    label = "My connected accounts"

    def __init__(self, db: Session, user: User):
        self._db = db
        self._user = user
        # Load the user's connected accounts once at construction.
        self._accounts: list[LinkedAccount] = list(
            db.scalars(
                select(LinkedAccount).where(
                    LinkedAccount.user_id == user.id,
                    LinkedAccount.status == "connected",
                )
            ).all()
        )
        # Owned content is fetched exactly once per scan; the per-query loop calls
        # us repeatedly, so emit on the first call and return [] thereafter.
        self._emitted = False

    def is_configured(self) -> bool:
        """Usable only when the user has at least one connected account."""
        return bool(self._accounts)

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        """Return all owned mentions on the first call, then ``[]``.

        ``query`` is intentionally ignored — there is no keyword for owned content.
        Never raises: per-account failures are caught and skipped.
        """
        if self._emitted:
            return []
        self._emitted = True

        # Use a DEDICATED session for all LinkedAccount token-refresh + status writes.
        # The owned connector runs LAST in the scan, sharing the pipeline's session
        # would mean our commits flush the in-progress (uncommitted) scan mentions —
        # breaking scan atomicity on failure. An isolated session keeps our writes
        # (token refresh, last_synced_at, expiry) independent of the scan transaction.
        own_db = SessionLocal()
        mentions: list[RawMention] = []
        try:
            accounts = list(
                own_db.scalars(
                    select(LinkedAccount).where(
                        LinkedAccount.user_id == self._user.id,
                        LinkedAccount.status == "connected",
                    )
                ).all()
            )
            for linked in accounts:
                try:
                    mentions.extend(self._fetch_account(own_db, linked, limit=limit))
                except Exception:
                    # Defensive: a misbehaving provider must never break the scan.
                    logger.warning(
                        "owned fetch failed for provider=%s linked=%s user=%s",
                        linked.provider, linked.id, self._user.id,
                    )
        finally:
            own_db.close()
        return mentions

    def _fetch_account(
        self, db: Session, linked: LinkedAccount, *, limit: int
    ) -> list[RawMention]:
        """Fetch one connected account's own content, handling token refresh.

        ``db`` is the connector's OWN isolated session (not the scan's). On
        ``TokenExpired`` the account is marked ``expired`` and skipped; on success
        ``last_synced_at`` is stamped. Returns ``[]`` for any non-fatal problem.
        """
        adapter = get_provider(linked.provider)
        if adapter is None:
            return []

        # Centralized refresh: may mint a new access token and persist it, or raise
        # TokenExpired (no valid/refreshable token) which we treat as "skip + mark".
        try:
            access_token = get_valid_token(db, linked)
        except TokenExpired:
            self._mark_expired(db, linked)
            return []
        except Exception:
            logger.warning(
                "token refresh failed for provider=%s linked=%s user=%s",
                linked.provider, linked.id, self._user.id,
            )
            return []

        if not access_token:
            self._mark_expired(db, linked)
            return []

        try:
            # Adapters read provider-specific context from **extra
            # (Reddit: external_handle; Mastodon: instance_url).
            mentions = adapter.fetch_own_content(
                access_token=access_token,
                limit=limit,
                external_handle=linked.external_handle,
                external_id=linked.external_id,
                instance_url=linked.instance_url,
            )
        except Exception:
            logger.warning(
                "fetch_own_content failed for provider=%s linked=%s user=%s",
                linked.provider, linked.id, self._user.id,
            )
            return []

        # Success — stamp the sync time and clear any prior error.
        self._stamp_synced(db, linked)
        return list(mentions or [])

    def _mark_expired(self, db: Session, linked: LinkedAccount) -> None:
        """Mark an account expired so the UI can prompt a re-link; best-effort."""
        try:
            linked.status = "expired"
            linked.last_error = "token expired"
            db.add(linked)
            db.commit()
        except Exception:
            db.rollback()

    def _stamp_synced(self, db: Session, linked: LinkedAccount) -> None:
        """Record a successful sync time; best-effort, never fatal."""
        try:
            linked.last_synced_at = datetime.now(timezone.utc)
            linked.last_error = None
            db.add(linked)
            db.commit()
        except Exception:
            db.rollback()
