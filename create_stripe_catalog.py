"""
One-time helper to create Products + Prices in your Stripe account.
Run locally with a restricted or test secret key:

    export STRIPE_SECRET_KEY=sk_test_...
    python src/create_stripe_catalog.py

Then copy the printed Price IDs into Fly secrets (STRIPE_PRICE_ID, STRIPE_PRICE_ID_SOVEREIGN).
"""
import os
import sys

import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
if not stripe.api_key:
    print("ERROR: Set STRIPE_SECRET_KEY environment variable first.", file=sys.stderr)
    sys.exit(1)


def build_odynex_catalog():
    print("[INFO] Constructing subscription models inside Stripe...")

    # 1. Axis Stream – metered / usage style (or fixed low-cost subscription)
    axis_stream = stripe.Product.create(
        name="Axis Stream (Odynex Core)",
        description=(
            "Real-time, usage-metered physics telemetry API. "
            "Perfect for drone fleets and autonomous logistics."
        ),
        metadata={"tier": "axis_stream"},
    )
    # Simple monthly subscription for Checkout demo; switch to metered Price for true usage billing
    axis_stream_price = stripe.Price.create(
        product=axis_stream.id,
        currency="usd",
        unit_amount=500,  # $5.00 / month starter
        recurring={"interval": "month"},
        nickname="Axis Stream Monthly",
    )
    print(f"[SUCCESS] Axis Stream. Product={axis_stream.id} Price={axis_stream_price.id}")

    # 2. Sovereign Gateway
    sovereign_gateway = stripe.Product.create(
        name="Sovereign Gateway Tier",
        description=(
            "Isolated localized regional cluster nodes. "
            "Designed for smart cities, municipal grids, and transit networks."
        ),
        metadata={"tier": "sovereign_gateway"},
    )
    sovereign_gateway_price = stripe.Price.create(
        product=sovereign_gateway.id,
        currency="usd",
        unit_amount=450000,  # $4,500.00
        recurring={"interval": "month"},
        nickname="Sovereign Gateway Monthly Base",
    )
    print(
        f"[SUCCESS] Sovereign Gateway. Product={sovereign_gateway.id} "
        f"Price={sovereign_gateway_price.id}"
    )

    print("\nSet these as Fly secrets:")
    print(f"  STRIPE_PRICE_ID={axis_stream_price.id}")
    print(f"  STRIPE_PRICE_ID_SOVEREIGN={sovereign_gateway_price.id}")


if __name__ == "__main__":
    build_odynex_catalog()
