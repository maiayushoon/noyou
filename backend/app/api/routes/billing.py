"""Stripe billing endpoints — checkout, customer portal, status, and webhook.

The authenticated endpoints (``GET /billing``, ``POST /billing/checkout``,
``POST /billing/portal``) let a logged-in user inspect and change their
subscription. The webhook (``POST /billing/webhook``) is called by Stripe (no
auth) and is the source of truth for plan changes — it reads the *raw* request
body so Stripe's signature can be verified byte-for-byte.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.database import get_db
from ...models.user import User
from ...schemas.billing import (
    BillingStatus,
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
)
from ...services import billing
from ..deps import get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])

# Plans a user can self-serve purchase through Checkout.
_PURCHASABLE_PLANS = {"pro", "premium"}


def _require_configured() -> None:
    """Raise 503 when Stripe isn't configured (no secret key present)."""
    if not billing.is_configured():
        raise HTTPException(status_code=503, detail="Billing is not configured")


@router.get("", response_model=BillingStatus)
def billing_status(
    current_user: User = Depends(get_current_user),
) -> BillingStatus:
    """Return the current user's plan and subscription state for the dashboard."""
    status_value = getattr(current_user, "subscription_status", None)
    return BillingStatus(
        plan=current_user.plan,
        subscription_status=status_value,
        has_active_subscription=status_value in billing.ACTIVE_STATUSES,
        publishable_key=getattr(settings, "stripe_publishable_key", "") or None,
    )


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout_session(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    """Start a Stripe Checkout Session for a pro/premium subscription."""
    _require_configured()
    plan = (payload.plan or "").lower()
    if plan not in _PURCHASABLE_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    url = billing.create_checkout(db, current_user, plan)
    return CheckoutResponse(url=url)


@router.post("/portal", response_model=PortalResponse)
def create_portal_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortalResponse:
    """Open the Stripe Billing Portal so the user can manage their subscription."""
    _require_configured()
    url = billing.create_portal(db, current_user)
    return PortalResponse(url=url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Receive and process a Stripe webhook (no auth — verified by signature).

    The raw request body is required so Stripe's signature can be checked
    byte-for-byte; we therefore read ``await request.body()`` rather than
    declaring a parsed Pydantic body. A signature failure surfaces as ``400``.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        billing.handle_webhook(db, payload, sig_header)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return {"received": True}
