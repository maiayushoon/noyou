from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class OrgIn(BaseModel):
    """Payload to create an organization."""

    name: str = Field(min_length=1, max_length=200, examples=["Acme Corp"])


class OrgOut(BaseModel):
    """An organization as seen by the requester, with their role in it."""

    id: str
    name: str
    owner_id: str
    created_at: datetime
    # The requesting user's role: "owner" for the owner, otherwise the member role.
    role: str

    model_config = {"from_attributes": True}


class MemberIn(BaseModel):
    """Payload to invite a member by email."""

    email: EmailStr


class MemberOut(BaseModel):
    """A member (invited or active) of an organization."""

    id: str
    email: str
    role: str
    status: str

    model_config = {"from_attributes": True}
