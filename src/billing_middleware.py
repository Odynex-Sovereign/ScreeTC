import stripe
import time

# Corporate Secret Key for Odynex Axis Logistics LLC
stripe.api_key = "sk_live_odynex_axis_logistics_prod_secret"

class OdynexBillingEngine:
    def __init__(self, unit_cost_usd=0.005):
        self.unit_cost_usd = unit_cost_usd

    def record_usage_and_charge(self, customer_stripe_id, frames_processed):
        """
        Bills the client instantly for the exact number of physics telemetry frames calculated.
        Routes corporate funds directly to account ending in 84.
        """
        if frames_processed <= 0:
            return None
            
        total_cents = int(frames_processed * (self.unit_cost_usd * 100))
        
        try:
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_stripe_id,
                amount=total_cents,
                currency="usd",
                description=f"ScreeTC Compute Metering: {frames_processed} Physics-ML Telemetry Tokens."
            )
            return invoice_item
        except stripe.error.StripeError as e:
            print(f"[METRIC ERROR] Financial transaction failed: {e}")
            return None
