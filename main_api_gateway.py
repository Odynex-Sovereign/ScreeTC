import json
import os
import time
from functools import wraps

import requests
import stripe
from flask import Flask, jsonify, request, send_from_directory

from billing_middleware import OdynexBillingEngine

app = Flask(__name__, static_folder="../public", static_url_path="")

# ---------------------------------------------------------------------------
# Configuration (all secrets from environment)
# ---------------------------------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")  # primary price for Axis Stream
STRIPE_PRICE_ID_SOVEREIGN = os.environ.get("STRIPE_PRICE_ID_SOVEREIGN", "")
APP_URL = os.environ.get("APP_URL", "http://localhost:8080").rstrip("/")
TRITON_CLUSTER_URL = os.environ.get(
    "TRITON_CLUSTER_URL",
    "http://127.0.0.1:8000/v1/models/screetc_pinn/infer",
)
UNIT_COST_USD = float(os.environ.get("UNIT_COST_USD", "0.005"))

billing_core = OdynexBillingEngine(unit_cost_usd=UNIT_COST_USD)

# In-memory idempotency store for webhook events (replace with Redis/DB in high scale)
_processed_events: set[str] = set()


# ---------------------------------------------------------------------------
# Health & static
# ---------------------------------------------------------------------------
@app.route("/health")
@app.route("/healthz")
def health():
    return jsonify({"status": "ok", "service": "screetc-api-gateway"}), 200


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/success")
def success_page():
    return send_from_directory(app.static_folder, "success.html")


# ---------------------------------------------------------------------------
# Stripe Checkout (server-side session creation)
# ---------------------------------------------------------------------------
@app.route("/v1/checkout", methods=["GET", "POST"])
def create_checkout_session():
    """Create a Stripe Checkout Session for the requested tier."""
    if not stripe.api_key:
        return jsonify({"status": "error", "message": "Stripe is not configured"}), 503

    tier = request.args.get("tier") or (request.get_json(silent=True) or {}).get("tier")
    if tier not in ("axis_stream", "sovereign_gateway"):
        return jsonify({"status": "error", "message": "Invalid or missing tier"}), 400

    price_id = STRIPE_PRICE_ID if tier == "axis_stream" else (STRIPE_PRICE_ID_SOVEREIGN or STRIPE_PRICE_ID)
    if not price_id:
        return jsonify({
            "status": "error",
            "message": "STRIPE_PRICE_ID (or STRIPE_PRICE_ID_SOVEREIGN) is not set",
        }), 503

    mode = "subscription"
    try:
        session = stripe.checkout.Session.create(
            mode=mode,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{APP_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{APP_URL}/?canceled=1",
            metadata={"tier": tier, "product": "screetc"},
            allow_promotion_codes=True,
        )
        # Browser redirect for GET from the landing page
        if request.method == "GET":
            return jsonify({"url": session.url, "session_id": session.id}), 200
        return jsonify({"url": session.url, "session_id": session.id}), 200
    except stripe.error.StripeError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/v1/checkout/redirect", methods=["GET"])
def checkout_redirect():
    """Convenience endpoint that issues a 303 redirect to Stripe Checkout."""
    resp = create_checkout_session()
    if isinstance(resp, tuple):
        body, status = resp[0], resp[1]
        data = body.get_json() if hasattr(body, "get_json") else body
        if status == 200 and data.get("url"):
            return "", 303, {"Location": data["url"]}
        return body, status
    return resp


# ---------------------------------------------------------------------------
# Stripe Webhook (signature verification + idempotent handling)
# ---------------------------------------------------------------------------
@app.route("/v1/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not STRIPE_WEBHOOK_SECRET:
        app.logger.error("STRIPE_WEBHOOK_SECRET is not configured")
        return jsonify({"error": "webhook not configured"}), 503

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({"error": "invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "invalid signature"}), 400

    event_id = event.get("id")
    if event_id in _processed_events:
        return jsonify({"status": "already_processed"}), 200

    event_type = event["type"]
    data_object = event["data"]["object"]

    try:
        if event_type == "checkout.session.completed":
            _handle_checkout_completed(data_object)
        elif event_type == "invoice.paid":
            _handle_invoice_paid(data_object)
        elif event_type == "customer.subscription.deleted":
            _handle_subscription_deleted(data_object)
        # Add more event types as needed
    except Exception as exc:
        app.logger.exception("Webhook handler error: %s", exc)
        # Return 500 so Stripe retries; do not mark as processed
        return jsonify({"error": "handler_failed"}), 500

    _processed_events.add(event_id)
    # Bound memory for the simple set
    if len(_processed_events) > 10_000:
        _processed_events.clear()

    return jsonify({"status": "ok"}), 200


def _handle_checkout_completed(session: dict) -> None:
    """Mark customer / subscription active after successful Checkout."""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    tier = (session.get("metadata") or {}).get("tier", "unknown")
    app.logger.info(
        "Checkout completed: customer=%s subscription=%s tier=%s",
        customer_id,
        subscription_id,
        tier,
    )
    # Persist entitlement if you add a DB later. For now Stripe is source of truth.


def _handle_invoice_paid(invoice: dict) -> None:
    customer_id = invoice.get("customer")
    app.logger.info("Invoice paid for customer=%s amount=%s", customer_id, invoice.get("amount_paid"))


def _handle_subscription_deleted(subscription: dict) -> None:
    customer_id = subscription.get("customer")
    app.logger.info("Subscription deleted for customer=%s", customer_id)


# ---------------------------------------------------------------------------
# Physics telemetry endpoint (existing behaviour, made resilient)
# ---------------------------------------------------------------------------
@app.route("/v1/flow", methods=["POST"])
def process_physics_telemetry():
    start_time = time.time()

    try:
        data = request.get_json(force=True, silent=True) or json.loads(request.data or b"{}")
    except Exception:
        return jsonify({"status": "error", "message": "Invalid JSON Payload"}), 400

    customer_stripe_id = data.get("customer_stripe_id")
    domain_points = data.get("domain_points")
    inlet_velocity = data.get("inlet_velocity_mps", 0.0)
    temperature_k = data.get("temperature_kelvin", 288.15)

    if not domain_points or not isinstance(domain_points, list):
        return jsonify({"status": "error", "message": "domain_points (list of [x,y,z]) is required"}), 400

    # 1. Enforce subscription / payment profile
    if not customer_stripe_id or not billing_core.verify_client_entitlement(customer_stripe_id):
        return jsonify({
            "status": "error",
            "message": "Access Denied: No active subscription or valid payment profile on file.",
        }), 401

    # 2. Format payload for Nvidia Triton (shape must be valid JSON)
    triton_payload = {
        "inputs": [
            {
                "name": "domain_points",
                "shape": [len(domain_points), 3],
                "datatype": "FP32",
                "data": domain_points,
            },
            {
                "name": "fluid_parameters",
                "shape": [1, 2],
                "datatype": "FP32",
                "data": [[float(inlet_velocity), float(temperature_k)]],
            },
        ]
    }

    # 3. Forward to Triton cluster (or graceful mock when unreachable)
    vector_field = None
    pressure_field = None
    used_mock = False
    try:
        triton_response = requests.post(
            TRITON_CLUSTER_URL,
            data=json.dumps(triton_payload),
            headers={"Content-Type": "application/json"},
            timeout=5.0,
        )
        triton_response.raise_for_status()
        triton_output = triton_response.json()
        vector_field = triton_output["outputs"][0]["data"]
        pressure_field = triton_output["outputs"][1]["data"]
    except Exception as e:
        # Production-safe fallback: return deterministic mock so payments & API surface stay usable
        # without a live GPU cluster. Set TRITON_CLUSTER_URL to a real endpoint to disable mock.
        app.logger.warning("Triton unreachable (%s); returning mock physics fields", e)
        used_mock = True
        n = len(domain_points)
        vector_field = [[0.0, float(inlet_velocity), 0.0] for _ in range(n)]
        pressure_field = [[101325.0] for _ in range(n)]

    # 4. Record usage charge
    billing_core.record_usage_and_charge(
        customer_stripe_id=customer_stripe_id, frames_processed=1
    )

    return jsonify({
        "status": "success",
        "compute_latency_ms": round((time.time() - start_time) * 1000, 2),
        "vector_field": vector_field,
        "pressure_field": pressure_field,
        "confidence_score": 0.9942 if not used_mock else 0.50,
        "mock_inference": used_mock,
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
