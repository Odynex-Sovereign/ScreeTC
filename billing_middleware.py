"""
Odynex billing engine — entitlement checks and usage recording.

Never hard-code Stripe keys. All secrets come from the environment.
In development (no STRIPE_SECRET_KEY) entitlement is granted for any
non-empty customer id so local demos work.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import stripe

logger = logging.getLogger("screetc.billing")


class OdynexBillingEngine:
    def __init__(self, unit_cost_usd: float = 0.005) -> None:
        self.unit_cost_usd = float(unit_cost_usd)
        # Ensure the library key is always taken from env (never hard-coded).
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY") or None

    def verify_client_entitlement(self, customer_stripe_id: str) -> bool:
        """Return True if the customer may call metered endpoints."""
        if not customer_stripe_id or not str(customer_stripe_id).strip():
            return False

        if not stripe.api_key:
            # Local / simulator mode: allow any non-empty id.
            logger.debug("Stripe not configured — granting demo entitlement")
            return True

        try:
            customer = stripe.Customer.retrieve(customer_stripe_id)
            if getattr(customer, "deleted", False):
                return False
            subs = stripe.Subscription.list(
                customer=customer_stripe_id, status="active", limit=1
            )
            return len(subs.data) > 0
        except stripe.error.StripeError as exc:
            logger.warning("Entitlement check failed: %s", exc)
            return False

    def record_usage_and_charge(
        self, customer_stripe_id: str, frames_processed: int
    ) -> dict[str, Any]:
        """Record usage. Returns a small receipt dict for the response."""
        frames = max(0, int(frames_processed))
        amount = round(frames * self.unit_cost_usd, 6)
        receipt: dict[str, Any] = {
            "frames_processed": frames,
            "unit_cost_usd": self.unit_cost_usd,
            "amount_usd": amount,
            "mode": "demo" if not stripe.api_key else "live",
        }

        if frames <= 0 or not stripe.api_key:
            return receipt

        try:
            stripe.InvoiceItem.create(
                customer=customer_stripe_id,
                amount=int(round(amount * 100)),  # cents
                currency="usd",
                description=f"ScreeTC Axis Stream — {frames} telemetry frame(s)",
            )
            receipt["recorded"] = True
        except stripe.error.StripeError as exc:
            logger.error("Usage recording failed: %s", exc)
            receipt["recorded"] = False
            receipt["error"] = str(exc)

        return receipt
