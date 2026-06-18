"""Request/response schemas for email verification and password reset."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    """Body for endpoints that accept an email address (resend / forgot)."""

    email: EmailStr


class TokenRequest(BaseModel):
    """Body for email verification — a single opaque token."""

    token: str = Field(min_length=1, max_length=64)


class ResetPasswordRequest(BaseModel):
    """Body for completing a password reset."""

    token: str = Field(min_length=1, max_length=64)
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    """Generic, non-revealing acknowledgement returned by these endpoints."""

    message: str
