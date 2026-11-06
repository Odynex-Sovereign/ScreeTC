# ScreeTC — Deploy guide (Fly.io + local)

## Why the previous deploy failed

Fly returned:

```text
GPU machines are no longer supported: config.guest.gpu_kind and config.guest.gpus must be unset
```

The old `fly.toml` requested an A10G GPU on the app machine. That path is no longer supported for this app type. **ScreeTC’s control plane (API + billing + simulator) does not need a GPU.** Real PINN inference belongs on a separate Triton/Modulus cluster or a private customer appliance.

## What changed

- `fly.toml` — CPU-only VM, health checks on `/healthz`, no `gpu_kind`
- `Dockerfile` — slim Python 3.12 image, non-root user, gunicorn
- `main_api_gateway.py` — clean env-only secrets, Stripe Checkout, simulator by default, Triton adapter when configured
- Modular integration simulators (industrial / market / energy / vehicle) — interfaces only, no vendor endorsement claims
- `.env.example`, `docker-compose.yml`, public landing + success pages

## Local run (under 5 minutes)

```bash
cp .env.example .env
# optional: add Stripe test keys for live checkout testing
docker compose up --build
# or:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export INFERENCE_MODE=simulator PORT=8080
python main_api_gateway.py
```

Open http://localhost:8080 — health at `/healthz`, pricing at `/pricing`.

### Test the physics API (simulator)

```bash
curl -s -X POST http://localhost:8080/v1/flow \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_stripe_id": "demo_customer",
    "domain_points": [[0,0,0],[1,0,0],[0,1,0]],
    "inlet_velocity_mps": 12.0,
    "temperature_kelvin": 290.0
  }' | jq .
```

## Fly deploy (CPU)

```bash
# From repo root, after committing the fixed files
flyctl deploy -a screetc --config fly.toml
```

Or with a pre-built image (after registry push):

```bash
flyctl deploy -a screetc --config fly.toml
```

Set secrets (required for live purchases):

```bash
flyctl secrets set -a screetc \
  STRIPE_SECRET_KEY=sk_live_... \
  STRIPE_WEBHOOK_SECRET=whsec_... \
  STRIPE_PRICE_ID=price_... \
  APP_URL=https://screetc.fly.dev
```

Optional:

```bash
flyctl secrets set -a screetc \
  STRIPE_PRICE_ID_SOVEREIGN=price_... \
  INFERENCE_MODE=simulator \
  UNIT_COST_USD=0.005
```

When you have a real Triton endpoint:

```bash
flyctl secrets set -a screetc \
  INFERENCE_MODE=triton \
  TRITON_CLUSTER_URL=https://your-triton-host/v2/models/screetc_pinn/infer
```

## Live purchases

1. Create products/prices in Stripe Dashboard (or run `create_stripe_catalog.py` with keys).
2. Set the secrets above.
3. Point Stripe webhook to `https://<your-app>/v1/webhook/stripe`.
4. Users hit **Start Axis Stream** → Stripe Checkout → success page.

Without Stripe keys the site still serves the landing page and simulator API for demos; checkout returns a clear 503.

## Enterprise / Siemens / Nasdaq / Hitachi / Tesla patterns

Adapters under `/v1/integrations/*` are **simulator implementations of vendor-neutral interfaces**. They do **not** claim live integration, certification, or endorsement. Production connections require customer credentials, contracts, and legal review.

## Contact

**David Fabian Cadelinia**  
Founder & Institutional Architect  
Odynex Axis Logistics LLC  
david@odynexaxis.biz · +1 229-364-1658 · https://www.odynexaxis.biz
