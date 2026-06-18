from __future__ import annotations

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    platform: str = Field(examples=["twitter", "google", "linkedin"])
    handle: str = Field(description="Handle, profile id, or search term to monitor")
    display_name: str | None = None
    profile_url: str | None = None


class AccountOut(BaseModel):
    id: str
    platform: str
    handle: str
    display_name: str | None = None
    profile_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}
