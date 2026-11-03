# CHANGES – Production readiness for Fly.io + Stripe

Every modification made to prepare the repository for secure production deployment.

## Summary

- Fixed syntax errors and broken payment paths
- Removed all hard-coded secrets
- Implemented Stripe Checkout (server-side) + signed webhooks with idempotent handling
- Added health checks, correct host/port binding, production Dockerfile & fly.toml
- Added `.env.example`, improved `.gitignore` / `.dockerignore`
- Served static landing pages from Flask
- Made Triton dependency optional (mock fallback) so the service is functional without a GPU cluster

---

## File-by-file

### `src/main_api_gateway.py` (rewritten)
- Fixed invalid JSON shape syntax (`"shape":,`)
- Removed hard-coded Stripe key and Triton URL
- All configuration read from environment variables
- Added `/health` and `/healthz`
- Serve static files from `public/` (`/`, `/success`)
- Added `/v1/checkout` – creates Stripe Checkout Session server-side
- Added `/v1/webhook/stripe` – signature verification + idempotent event handling
- Graceful mock inference when Triton is unreachable (keeps payments & API usable)
- Correct Gunicorn entrypoint compatibility

### `src/billing_middleware.py` (rewritten)
- Removed hard-coded live secret key
- Reads `STRIPE_SECRET_KEY` from environment
- Renamed primary method to `verify_client_entitlement` (kept old misspelled alias)
- Safer handling when Stripe is not configured (local/dev)

### `src/create_stripe_catalog.py` (rewritten)
- No hard-coded keys
- Creates usable monthly Prices suitable for Checkout
- Prints the Price IDs to set as Fly secrets

### `Dockerfile` (replaced)
- Removed duplicated multi-stage garbage
- Python 3.11-slim, non-root user, healthcheck
- Correct Gunicorn bind to `0.0.0.0:8080`
- Only copies runtime assets

### `fly.toml` (replaced)
- Modern `[http_service]` syntax
- HTTP health check on `/health`
- `force_https`, concurrency limits, sensible VM size
- Secrets left out of the file (set via `fly secrets set`)

### `.dockerignore` (replaced)
- Excludes secrets, git, docs, and non-runtime files

### `.gitignore` (updated)
- Stronger secret patterns (`.env*`, keys, credentials)
- Model weight extensions

### `.env.example` (new)
- Documents every required and optional variable

### `requirements.txt` (updated)
- Pinned slightly newer compatible versions of flask, stripe, gunicorn, requests

### `Procfile` (fixed)
- Correct Gunicorn module path and PORT handling

### `public/index.html` (updated)
- Calls `/v1/checkout` via fetch and redirects to Stripe-hosted page
- Clear error surface when Checkout is misconfigured

### `public/success.html` (updated)
- Removes fake hard-coded token; shows session_id from query string
- Accurate messaging for Stripe-linked accounts

### Documentation (new)
- `README-DEPLOY.md` – exact Fly + Stripe commands
- `CHANGES.md` – this file
- `PRE_DEPLOY_CHECKLIST.md` – pre-flight list

---

## Intentionally unchanged

- `models/screetc_pinn/config.pbtxt` – Triton model config (reference)
- `nginx.conf`, `docker-compose.yml` – local GPU/Triton stack (optional)
- `NDA.md`, `LICENSE`, `stripe_payout_routing.json` – legal / payout metadata (no secrets of use; routing numbers are public ABA numbers)
- Core `/v1/flow` contract (request/response shape) preserved; only made resilient
