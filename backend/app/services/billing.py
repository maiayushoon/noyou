"""Stripe billing service — checkout, customer portal, and webhook handling.

This is the single integration point with Stripe. The official ``stripe`` Python
SDK is imported lazily (inside ``_stripe()``) so the module imports cleanly even
when the package isn't installed or no keys are configured — pure-logic helpers
(``price_for_plan`` / ``plan_for_price``) and the ``is_configured`` guard remain
importable and testable without the SDK or network access.

Flow:
  * ``create_checkout`` starts a subscription Checkout Session for pro/premium.
  * ``create_portal`` opens Stripe's hosted Billing Portal so users can manage
    or cancel their subscription.
  * ``handle_webhook`` is the source of truth for plan changes: Stripe calls our
    webhook on checkout completion and subscription updates/deletes, and we
    reconcile ``user.plan`` / ``user.subscription_status`` from those events.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.user import User

# Subscription statuses that grant access to a paid plan.
ACTIVE_STATUSES = {"active", "trialing"}


def _stripe() -> Any:
    """Import the Stripe SDK lazily and apply the configured secret key.

    Kept out of module scope so importing this module never hard-depends on the
    ``stripe`` package being installed (e.g. in test environments that exercise
    only the pure-logic helpers and the ``503 not configured`` paths).
    """
    import stripe  # noqa: PLC0415 — intentional lazy import

    stripe.api_key = getattr(settings, "stripe_secret_key", "")
    return stripe


def is_configured() -> bool:
    """Whether a Stripe secret key is present (billing can talk to Stripe)."""
    return bool(getattr(settings, "stripe_secret_key", ""))


# --- Price <-> plan mapping ------------------------------------------------
def price_for_plan(plan: str) -> str | None:
    """Return the configured Stripe price id for a plan name, or ``None``.

    Maps ``pro``/``premium`` (and ``enterprise`` if its price is configured) to
    their ``settings.stripe_price_*`` values. Unknown/unconfigured plans yield
    ``None`` so callers can reject them before touching Stripe.
    """
    mapping: dict[str, str] = {
        "pro": getattr(settings, "stripe_price_pro", ""),
        "premium": getattr(settings, "stripe_price_premium", ""),
    }
    enterprise_price = getattr(settings, "stripe_price_enterprise", "")
    if enterprise_price:
        mapping["enterprise"] = enterprise_price
    price = mapping.get((plan or "").lower())
    return price or None


def plan_for_price(price_id: str | None) -> str:
    """Reverse-map a Stripe price id to a plan name, defaulting to ``free``.

    Used by the webhook to translate a subscription's price back into the plan
    we store on the user. Unknown / missing price ids fall back to ``free`` so a
    stray event can never silently grant a paid tier.
    """
    if not price_id:
        return "free"
    reverse: dict[str, str] = {}
    price_pro = getattr(settings, "stripe_price_pro", "")
    price_premium = getattr(settings, "stripe_price_premium", "")
    if price_pro:
        reverse[price_pro] = "pro"
    if price_premium:
        reverse[price_premium] = "premium"
    enterprise_price = getattr(settings, "stripe_price_enterprise", "")
    if enterprise_price:
        reverse[enterprise_price] = "enterprise"
    return reverse.get(price_id, "free")


# --- Customer / checkout / portal ------------------------------------------
def get_or_create_customer(db: Session, user: User) -> str:
    """Return the user's Stripe customer id, creating the customer if needed.

    The id is persisted on ``user.stripe_customer_id`` so subsequent checkout
    and portal sessions reuse the same customer (and so webhooks can resolve the
    user back from the customer id).
    """
    existing = getattr(user, "stripe_customer_id", None)
    if existing:
        return existing

    stripe = _stripe()
    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": str(user.id)},
    )
    user.stripe_customer_id = customer.id
    db.add(user)
    db.commit()
    return customer.id


def create_checkout(db: Session, user: User, plan: str) -> str:
    """Create a subscription Checkout Session and return its redirect URL."""
    price_id = price_for_plan(plan)
    if not price_id:
        # No configured price for this plan — treat as a configuration problem.
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Billing is not configured")

    stripe = _stripe()
    customer_id = get_or_create_customer(db, user)
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing?status=success",
        cancel_url=f"{settings.frontend_url}/billing?status=cancelled",
        client_reference_id=str(user.id),
        allow_promotion_codes=True,
    )
    return session.url


def create_portal(db: Session, user: User) -> str:
    """Create a Billing Portal Session and return its redirect URL."""
    stripe = _stripe()
    customer_id = get_or_create_customer(db, user)
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.frontend_url}/billing",
    )
    return session.url


# --- Webhook ---------------------------------------------------------------
def _resolve_user(
    db: Session, customer_id: str | None, client_reference_id: str | None
) -> User | None:
    """Find the user a webhook event refers to.

    Prefers the Stripe customer id (set the first time we created the customer),
    falling back to ``client_reference_id`` (the user id we stamped on the
    Checkout Session). Returns ``None`` when neither resolves — the caller then
    ignores the event rather than mutating a random user.
    """
    if customer_id:
        user = db.scalar(select(User).where(User.stripe_customer_id == customer_id))
        if user:
            return user
    if client_reference_id:
        return db.get(User, client_reference_id)
    return None


def _price_id_from_subscription(subscription: dict[str, Any]) -> str | None:
    """Pull the first line-item price id out of a subscription object."""
    items = (subscription.get("items") or {}).get("data") or []
    if not items:
        return None
    price = items[0].get("price") or {}
    return price.get("id")


def _apply_subscription(db: Session, user: User, subscription: dict[str, Any]) -> None:
    """Set the user's plan/status/subscription id from a subscription object."""
    price_id = _price_id_from_subscription(subscription)
    user.plan = plan_for_price(price_id)
    user.stripe_subscription_id = subscription.get("id")
    user.subscription_status = subscription.get("status")
    db.add(user)
    db.commit()


def handle_webhook(db: Session, payload: bytes, sig_header: str) -> None:
    """Verify and process a Stripe webhook event.

    Verifies the signature against ``settings.stripe_webhook_secret`` and updates
    the relevant user on the events we care about:

      * ``checkout.session.completed`` — a new subscription was purchased.
      * ``customer.subscription.updated`` — plan/status changed (upgrade,
        cancellation scheduled, payment recovered, ...).
      * ``customer.subscription.deleted`` — subscription ended; revert to free.

    Defensive by design: unknown event types and events that don't resolve to a
    known user are ignored. A failed signature check raises ``ValueError`` so the
    route can return ``400``.
    """
    stripe = _stripe()
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except Exception as exc:  # signature / parse failure
        raise ValueError("Invalid webhook signature") from exc

    event_type = event.get("type")
    data_object = (event.get("data") or {}).get("object") or {}

    if event_type == "checkout.session.completed":
        user = _resolve_user(
            db,
            data_object.get("customer"),
            data_object.get("client_reference_id"),
        )
        if user is None:
            return
        # Persist the customer id if we didn't already have it, so future
        # subscription.* events (which only carry the customer) resolve.
        if not getattr(user, "stripe_customer_id", None) and data_object.get("customer"):
            user.stripe_customer_id = data_object.get("customer")

        subscription_id = data_object.get("subscription")
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            _apply_subscription(db, user, dict(subscription))
        else:
            db.add(user)
            db.commit()
        return

    if event_type in ("customer.subscription.updated", "customer.subscription.created"):
        user = _resolve_user(db, data_object.get("customer"), None)
        if user is None:
            return
        _apply_subscription(db, user, data_object)
        return

    if event_type == "customer.subscription.deleted":
        user = _resolve_user(db, data_object.get("customer"), None)
        if user is None:
            return
        user.plan = "free"
        user.subscription_status = data_object.get("status") or "canceled"
        user.stripe_subscription_id = None
        db.add(user)
        db.commit()
        return

    # Unknown / uninteresting event — ignore.
    return
