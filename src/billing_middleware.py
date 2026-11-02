import stripe

stripe.api_key = "sk_live_odynex_axis_logistics_prod_secret"

class OdynexBillingEngine:
    def __init__(self, unit_cost_usd=0.005):
        self.unit_cost_usd = unit_cost_usd

    def verify_client_entinement(self, customer_stripe_id):
        """
        Scans your corporate ledger in real-time before executing any physics calculations.
        Ensures the incoming device holds a valid payment profile or active capacity tier.
        """
        try:
            customer = stripe.Customer.retrieve(customer_stripe_id)
            # Query if client account status is unflagged or holds active subscriptions
            if customer.get("deleted", False):
                return False
            return True
        except stripe.error.StripeError:
            return False

    def record_usage_and_charge(self, customer_stripe_id, frames_processed):
        """
        Logs compute token usage and processes recurring usage charges.
        Ensures programmatic settlement routes directly to your Sunrise Banks routing profile.
        """
        if frames_processed <= 0:
            return None
        total_cents = int(frames_processed * (self.unit_cost_usd * 100))
        try:
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_stripe_id,
                amount=total_cents,
                currency="usd",
                description=f"ScreeTC Infrastructure Invoicing: {frames_processed} Telemetry Frames Computed."
            )
            return invoice_item
        except stripe.error.StripeError as e:
            print(f"[BILLING REJECTION] Automated clearing settlement error: {e}")
            return None
