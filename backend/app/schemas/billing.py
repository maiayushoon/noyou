"""Pydantic request/response models for the Stripe billing endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    """Body for ``POST /billing/checkout`` — the plan the user wants to buy."""

    plan: str


class CheckoutResponse(BaseModel):
    """A Stripe Checkout Session URL to redirect the browser to."""

    url: str


class PortalResponse(BaseModel):
    """A Stripe Billing Portal URL to redirect the browser to."""

    url: str


class BillingStatus(BaseModel):
    """The current user's billing state, surfaced to the dashboard.

    ``has_active_subscription`` is a convenience flag derived from
    ``subscription_status`` (true while the subscription is ``active`` or
    ``trialing``). ``publishable_key`` is the Stripe publishable key (safe to
    expose to the browser) or ``None`` when billing is not configured.
    """

    plan: str
    subscription_status: str | None = None
    has_active_subscription: bool = False
    publishable_key: str | None = None
