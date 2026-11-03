import os
import stripe

# Never hard-code keys. Caller (main_api_gateway) sets stripe.api_key from env.
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


class OdynexBillingEngine:
    def __init__(self, unit_cost_usd: float = 0.005):
        self.unit_cost_usd = unit_cost_usd

    def verify_client_entitlement(self, customer_stripe_id: str) -> bool:
        """
        Returns True if the Stripe customer exists and is not deleted.
        For stricter gating, also check active subscriptions.
        """
        if not stripe.api_key:
            # In local/dev without Stripe, allow through so the API remains testable
            return bool(customer_stripe_id)

        try:
            customer = stripe.Customer.retrieve(customer_stripe_id)
            if customer.get("deleted", False):
                return False

            # Prefer an active subscription when present
            subs = stripe.Subscription.list(
                customer=customer_stripe_id, status="active", limit=1
            )
            if subs.data:
                return True

            # Fall back to "customer exists" for metered / invoice-item flows
            return True
        except stripe.error.StripeError:
            return False

    # Keep the original (misspelled) name as an alias so any external callers still work
    verify_client_entinement = verify_client_entitlement

    def record_usage_and_charge(self, customer_stripe_id: str, frames_processed: int):
        """
        Appends an invoice item for usage. For production metered billing prefer
        Stripe Usage Records / Meters against a metered Price.
        """
        if frames_processed <= 0 or not stripe.api_key:
            return None

        total_cents = int(frames_processed * (self.unit_cost_usd * 100))
        if total_cents <= 0:
            total_cents = 1  # Stripe minimum

        try:
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_stripe_id,
                amount=total_cents,
                currency="usd",
                description=(
                    f"ScreeTC Infrastructure Invoicing: "
                    f"{frames_processed} Telemetry Frame(s) Computed."
                ),
            )
            return invoice_item
        except stripe.error.StripeError as e:
            print(f"[BILLING REJECTION] Automated clearing settlement error: {e}")
            return None
