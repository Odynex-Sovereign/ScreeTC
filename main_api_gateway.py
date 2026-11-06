"""
ScreeTC API Gateway — production control plane.

- Stripe Checkout for live purchases (when keys are configured)
- Deterministic physics simulator (default) or Triton adapter
- Health, pricing, contact, and modular enterprise simulator endpoints
- No hard-coded secrets. Fail closed when required production config is missing.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests
import stripe
from flask import Flask, jsonify, request, send_from_directory

from billing_middleware import OdynexBillingEngine
from integrations import (
    get_energy_provider,
    get_industrial_provider,
    get_market_provider,
    get_vehicle_provider,
)
from physics_simulator import mock_latency_ms, simulate_flow_field

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("screetc")

app = Flask(__name__, static_folder="public", static_url_path="")

# ---------------------------------------------------------------------------
# Configuration (environment only)
# ---------------------------------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY") or None
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
STRIPE_PRICE_ID_SOVEREIGN = os.environ.get("STRIPE_PRICE_ID_SOVEREIGN", "")
APP_URL = (os.environ.get("APP_URL") or "http://localhost:8080").rstrip("/")
TRITON_CLUSTER_URL = os.environ.get("TRITON_CLUSTER_URL", "").rstrip("/")
INFERENCE_MODE = (os.environ.get("INFERENCE_MODE") or "simulator").lower()
UNIT_COST_USD = float(os.environ.get("UNIT_COST_USD", "0.005"))
PORT = int(os.environ.get("PORT", "8080"))

billing_core = OdynexBillingEngine(unit_cost_usd=UNIT_COST_USD)
_processed_events: set[str] = set()


# ---------------------------------------------------------------------------
# Health & static
# ---------------------------------------------------------------------------
@app.route("/health")
@app.route("/healthz")
def healthz():
    return jsonify(
        {
            "status": "ok",
            "service": "screetc-api-gateway",
            "inference_mode": INFERENCE_MODE,
            "stripe_configured": bool(stripe.api_key and STRIPE_PRICE_ID),
        }
    ), 200


@app.route("/")
def index():
    # Prefer public/index.html; fall back to root index.html if present
    try:
        return send_from_directory(app.static_folder, "index.html")
    except Exception:
        return send_from_directory(".", "index.html")


@app.route("/success")
def success_page():
    try:
        return send_from_directory(app.static_folder, "success.html")
    except Exception:
        return send_from_directory(".", "success.html")


@app.route("/pricing")
def pricing():
    return jsonify(
        {
            "tiers": [
                {
                    "id": "axis_stream",
                    "name": "Axis Stream",
                    "model": "metered",
                    "unit_cost_usd": UNIT_COST_USD,
                    "description": "Multi-tenant public API — per telemetry frame",
                },
                {
                    "id": "sovereign_gateway",
                    "name": "Sovereign Gateway",
                    "model": "subscription",
                    "base_usd_month": 4500,
                    "description": "Region-isolated clusters for municipalities and logistics",
                },
                {
                    "id": "odynex_core",
                    "name": "Odynex Core",
                    "model": "enterprise_contract",
                    "description": "Air-gapped private appliance — custom contract + NDA",
                },
            ],
            "contact": {
                "name": "David Fabian Cadelinia",
                "title": "Founder & Institutional Architect",
                "company": "Odynex Axis Logistics LLC",
                "email": "david@odynexaxis.biz",
                "phone": "+1 229-364-1658",
                "web": "https://www.odynexaxis.biz",
            },
        }
    )


@app.route("/contact")
def contact():
    return jsonify(
        {
            "name": "David Fabian Cadelinia",
            "title": "Founder & Institutional Architect",
            "company": "Odynex Axis Logistics LLC",
            "email": "david@odynexaxis.biz",
            "phone": "+1 229-364-1658",
            "web": "https://www.odynexaxis.biz",
            "note": "Enterprise, NDA, and private-deployment requests are handled by a human.",
        }
    )


# ---------------------------------------------------------------------------
# Stripe Checkout (live purchases when configured)
# ---------------------------------------------------------------------------
@app.route("/v1/checkout", methods=["GET", "POST"])
def create_checkout_session():
    if not stripe.api_key:
        return jsonify(
            {
                "status": "error",
                "message": "Stripe is not configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID.",
            }
        ), 503

    tier = request.args.get("tier") or (request.get_json(silent=True) or {}).get("tier")
    if tier not in ("axis_stream", "sovereign_gateway"):
        return jsonify({"status": "error", "message": "Invalid or missing tier"}), 400

    price_id = (
        STRIPE_PRICE_ID if tier == "axis_stream" else (STRIPE_PRICE_ID_SOVEREIGN or STRIPE_PRICE_ID)
    )
    if not price_id:
        return jsonify(
            {
                "status": "error",
                "message": "STRIPE_PRICE_ID (or STRIPE_PRICE_ID_SOVEREIGN) is not set",
            }
        ), 503

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{APP_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{APP_URL}/?canceled=1",
            metadata={"tier": tier, "product": "screetc"},
            allow_promotion_codes=True,
        )
        return jsonify({"url": session.url, "session_id": session.id}), 200
    except stripe.error.StripeError as exc:
        logger.exception("Checkout session failed")
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.route("/v1/checkout/redirect", methods=["GET"])
def checkout_redirect():
    """303 redirect helper for simple HTML buttons."""
    resp = create_checkout_session()
    if isinstance(resp, tuple):
        body, status = resp[0], resp[1]
        data = body.get_json(silent=True) if hasattr(body, "get_json") else None
        if status == 200 and data and data.get("url"):
            return "", 303, {"Location": data["url"]}
        return body, status
    return resp


@app.route("/v1/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    if not STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured")
        return jsonify({"status": "error", "message": "Webhook not configured"}), 503

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"status": "error", "message": "Invalid signature"}), 400

    event_id = event.get("id", "")
    if event_id in _processed_events:
        return jsonify({"status": "ok", "duplicate": True}), 200
    _processed_events.add(event_id)

    etype = event.get("type")
    logger.info("Stripe event: %s", etype)
    # Extend here: provision API keys, update entitlements, send welcome email, etc.
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Core physics API
# ---------------------------------------------------------------------------
@app.route("/v1/flow", methods=["POST"])
def process_physics_telemetry():
    start = time.time()
    data = request.get_json(silent=True) or {}

    customer_stripe_id = (data.get("customer_stripe_id") or "").strip()
    domain_points = data.get("domain_points") or []
    inlet_velocity = float(data.get("inlet_velocity_mps", 10.0))
    temperature_k = float(data.get("temperature_kelvin", 288.15))

    if not isinstance(domain_points, list):
        return jsonify({"status": "error", "message": "domain_points must be a list"}), 400

    if not billing_core.verify_client_entitlement(customer_stripe_id):
        return jsonify(
            {
                "status": "error",
                "message": "Access denied: no active subscription or valid payment profile.",
            }
        ), 401

    try:
        if INFERENCE_MODE == "triton" and TRITON_CLUSTER_URL:
            result = _call_triton(domain_points, inlet_velocity, temperature_k)
        else:
            result = simulate_flow_field(domain_points, inlet_velocity, temperature_k)
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception as exc:
        logger.exception("Inference failed")
        return jsonify({"status": "error", "message": f"Inference error: {exc}"}), 502

    n = len(domain_points)
    receipt = billing_core.record_usage_and_charge(customer_stripe_id, frames_processed=1)
    elapsed_ms = round((time.time() - start) * 1000, 2)

    return jsonify(
        {
            "status": "ok",
            "vector_field": result.get("vector_field"),
            "pressure_field": result.get("pressure_field"),
            "meta": {
                **(result.get("meta") or {}),
                "latency_ms": elapsed_ms,
                "estimated_latency_ms": mock_latency_ms(n),
                "billing": receipt,
            },
        }
    ), 200


def _call_triton(
    domain_points: list, inlet_velocity: float, temperature_k: float
) -> dict[str, Any]:
    """Forward to a real Triton endpoint when configured."""
    payload = {
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
    resp = requests.post(
        TRITON_CLUSTER_URL,
        json=payload,
        timeout=10.0,
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    body = resp.json()
    outputs = {o["name"]: o["data"] for o in body.get("outputs", [])}
    return {
        "vector_field": outputs.get("vector_field") or outputs.get("outputs") or [],
        "pressure_field": outputs.get("pressure_field") or [],
        "meta": {"mode": "triton", "points": len(domain_points)},
    }


# ---------------------------------------------------------------------------
# Modular enterprise simulators (interfaces only — no vendor claims)
# ---------------------------------------------------------------------------
@app.route("/v1/integrations/industrial/sensors", methods=["POST"])
def industrial_sensors():
    data = request.get_json(silent=True) or {}
    assets = data.get("asset_ids") or ["demo-asset-1"]
    provider = get_industrial_provider()
    return jsonify({"status": "ok", "readings": provider.read_sensors(assets)})


@app.route("/v1/integrations/market/quotes", methods=["POST"])
def market_quotes():
    data = request.get_json(silent=True) or {}
    symbols = data.get("symbols") or ["DEMO"]
    provider = get_market_provider()
    return jsonify(
        {
            "status": "ok",
            "quotes": provider.get_quotes(symbols),
            "disclaimer": "Simulated/delayed data only. Not for trading or investment advice.",
        }
    )


@app.route("/v1/integrations/energy/site", methods=["POST"])
def energy_site():
    data = request.get_json(silent=True) or {}
    provider = get_energy_provider()
    return jsonify({"status": "ok", "site": provider.get_site_power(data.get("site_id", "demo-site"))})


@app.route("/v1/integrations/vehicle/fleet", methods=["POST"])
def vehicle_fleet():
    data = request.get_json(silent=True) or {}
    provider = get_vehicle_provider()
    return jsonify(
        {"status": "ok", "fleet": provider.get_fleet_snapshot(data.get("fleet_id", "demo-fleet"))}
    )


# ---------------------------------------------------------------------------
# Local entrypoint (gunicorn used in production)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=os.environ.get("FLASK_DEBUG") == "1")
