import stripe

# Production Key Profile Configuration
stripe.api_key = "sk_live_odynex_axis_logistics_prod_secret"

def build_odynex_catalog():
    print("[INFO] Constructing subscription models inside Stripe Ledger Core...")

    # 1. Tier One: Axis Stream (Pay-As-You-Go Physics Telemetry Tokens)
    axis_stream = stripe.Product.create(
        name="Axis Stream (Odynex Core)",
        description="Real-time, usage-metered physics telemetry API. Perfect for drone fleets and autonomous logistics.",
        metadata={"tier": "axis_stream"}
    )
    axis_stream_price = stripe.Price.create(
        product=axis_stream.id,
        currency="usd",
        billing_scheme="per_unit",
        unit_amount=0, # Base token validation setup
        recurring={"interval": "month", "usage_type": "metered"},
        nickname="Axis Stream Metered Unit"
    )
    print(f"[SUCCESS] Axis Stream Online. Price ID: {axis_stream_price.id}")

    # 2. Tier Two: Sovereign Gateway (Fixed High-Volume Regional Compute Capacity)
    sovereign_gateway = stripe.Product.create(
        name="Sovereign Gateway Tier",
        description="Isolated localized regional cluster nodes. Designed for smart cities, municipal grids, and transit networks.",
        metadata={"tier": "sovereign_gateway"}
    )
    sovereign_gateway_price = stripe.Price.create(
        product=sovereign_gateway.id,
        currency="usd",
        unit_amount=450000, # Billed explicitly at $4,500.00 USD
        recurring={"interval": "month", "usage_type": "licensed"},
        nickname="Sovereign Gateway Monthly Base"
    )
    print(f"[SUCCESS] Sovereign Gateway Online. Price ID: {sovereign_gateway_price.id}")

if __name__ == "__main__":
    build_odynex_catalog()
