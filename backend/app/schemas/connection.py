"""Pydantic v2 schemas for the Connections (OAuth account-linking) feature.

These intentionally NEVER expose the encrypted token columns (``access_token_enc`` /
``refresh_token_enc``). Tokens are read at call time from the DB, decrypted in
memory, and used only as an Authorization header — they never serialize out of the
API.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator


def _split_scopes(value) -> list[str]:
    """Turn the stored space-delimited scope string into a list (empty -> [])."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [str(s) for s in value if s]
    return [s for s in str(value).split() if s]


class ConnectionOut(BaseModel):
    """A linked account as seen by its owner. No token fields, ever."""

    id: str
    provider: str
    status: str
    external_handle: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    instance_url: str | None = None
    scopes: list[str] = []
    last_synced_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("scopes", mode="before")
    @classmethod
    def _scopes_to_list(cls, value):
        # The DB stores scopes space-delimited; expose them as a list.
        return _split_scopes(value)


class ConnectStartOut(BaseModel):
    """Returned by ``POST /connections/{provider}/connect`` — where to send the user."""

    authorize_url: str


class ProviderInfo(BaseModel):
    """One provider card for the Connections UI."""

    provider: str
    label: str
    configured: bool
    connected: bool
    scopes_requested: list[str] = []
