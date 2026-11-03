# ScreeTC – Production Deployment Guide (Fly.io + Stripe)

This guide deploys the ScreeTC API Gateway to [Fly.io](https://fly.io) with secure Stripe Checkout and webhooks.

## Prerequisites

- A [Fly.io](https://fly.io) account
- A [Stripe](https://stripe.com) account (start in **Test mode**)
- `fly` CLI and `git` installed locally

---

## 1. Install the Fly CLI

```bash
# macOS / Linux
curl -L https://fly.io/install.sh | sh

# Or via Homebrew
brew install flyctl
```

Verify:

```bash
fly version
```

---

## 2. Log in

```bash
fly auth login
```

---

## 3. Create the Fly app

From the repository root:

```bash
cd ScreeTC
fly apps create screetc --org personal   # or your org
# If the name is taken, choose another and update fly.toml `app = "..."`
```

Optional: set the primary region (default in `fly.toml` is `dfw`):

```bash
fly regions set dfw
```

---

## 4. Create Stripe products & prices (one-time)

In **Stripe Test mode**:

```bash
export STRIPE_SECRET_KEY=sk_test_...
python src/create_stripe_catalog.py
```

Copy the printed `price_...` IDs. You will set them as secrets next.

Alternatively create Products/Prices in the Stripe Dashboard and copy the Price IDs.

---

## 5. Set secrets

```bash
fly secrets set \
  STRIPE_SECRET_KEY="sk_test_xxxxxxxx" \
  STRIPE_WEBHOOK_SECRET="whsec_xxxxxxxx" \
  STRIPE_PRICE_ID="price_xxxxxxxx" \
  STRIPE_PRICE_ID_SOVEREIGN="price_yyyyyyyy" \
  APP_URL="https://screetc.fly.dev"
```

Optional:

```bash
fly secrets set TRITON_CLUSTER_URL="https://your-triton-host/v1/models/screetc_pinn/infer"
fly secrets set UNIT_COST_USD="0.005"
```

List secrets (values are never shown):

```bash
fly secrets list
```

---

## 6. Deploy

```bash
fly deploy
```

Watch logs:

```bash
fly logs
```

Open the app:

```bash
fly open
# or
curl -s https://screetc.fly.dev/health
```

---

## 7. Configure the Stripe webhook

1. In Stripe Dashboard → **Developers → Webhooks → Add endpoint**.
2. Endpoint URL:

   ```
   https://screetc.fly.dev/v1/webhook/stripe
   ```

3. Events to send (minimum):

   - `checkout.session.completed`
   - `invoice.paid`
   - `customer.subscription.deleted`

4. After creation, reveal the **Signing secret** (`whsec_...`) and update Fly:

   ```bash
   fly secrets set STRIPE_WEBHOOK_SECRET="whsec_xxxxxxxx"
   ```

5. Stripe will automatically re-deliver after the secret is updated on the next event; you can also send a test event from the Dashboard.

---

## 8. Test payments (Stripe Test mode)

1. Open `https://screetc.fly.dev/`.
2. Click **Provision API Core** (or Sovereign).
3. Use a [Stripe test card](https://stripe.com/docs/testing):

   - Card: `4242 4242 4242 4242`
   - Any future expiry, any CVC, any ZIP.

4. After success you land on `/success`.
5. Confirm in Stripe Dashboard → Payments / Customers that the session completed.
6. Confirm webhook delivery under the webhook endpoint’s “Events” tab (HTTP 200).

Call the physics API (replace with a real `cus_...` from the Dashboard):

```bash
curl -s -X POST https://screetc.fly.dev/v1/flow \
  -H "Content-Type: application/json" \
  -d '{
    "customer_stripe_id": "cus_xxxxxxxx",
    "domain_points": [[1.0,0.0,0.0],[1.1,0.1,0.0]],
    "inlet_velocity_mps": 12.0,
    "temperature_kelvin": 288.15
  }' | jq .
```

If Triton is not configured, the response includes `"mock_inference": true` and still returns fields.

---

## 9. Switch safely to Live mode

1. In Stripe Dashboard switch to **Live mode**.
2. Create live Products/Prices (or re-run `create_stripe_catalog.py` with a **live** secret key).
3. Create a **new** webhook endpoint pointing at the same URL (live mode has its own signing secret).
4. Update Fly secrets with **live** values:

   ```bash
   fly secrets set \
     STRIPE_SECRET_KEY="sk_live_..." \
     STRIPE_WEBHOOK_SECRET="whsec_..." \
     STRIPE_PRICE_ID="price_..." \
     STRIPE_PRICE_ID_SOVEREIGN="price_..." \
     APP_URL="https://screetc.fly.dev"
   ```

5. `fly deploy` is **not** required when only secrets change; machines pick up new secrets on next restart. Force a restart if needed:

   ```bash
   fly apps restart screetc
   ```

6. Run a small live transaction with a real card, then verify webhook delivery and Dashboard records.

**Never** mix test and live keys in the same environment.

---

## 10. Useful Fly commands

```bash
fly status
fly logs
fly ssh console
fly scale count 1
fly secrets list
fly apps restart screetc
```

---

## Architecture notes

| Component | Role |
|-----------|------|
| Flask + Gunicorn | HTTP API, Checkout session creation, webhook receiver, static landing pages |
| Stripe Checkout | Hosted payment UI (PCI scope stays with Stripe) |
| Stripe Webhooks | Server-side confirmation of payment / subscription state |
| Triton (optional) | GPU inference; when unreachable a deterministic mock is returned so the app stays usable |
| Fly.io | TLS termination, health checks, secrets, auto-start machines |

No application database is required for the current design: Stripe is the source of truth for customers and subscriptions. For high-scale idempotency of webhooks, replace the in-memory event set with Redis or Postgres.
