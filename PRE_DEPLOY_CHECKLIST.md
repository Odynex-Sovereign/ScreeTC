# Pre-Deploy Checklist – ScreeTC

Complete every item before pointing real traffic or live Stripe keys at the deployment.

## Code & build

- [ ] `python -m py_compile src/main_api_gateway.py src/billing_middleware.py src/create_stripe_catalog.py`
- [ ] No hard-coded `sk_live_`, `sk_test_`, or `whsec_` strings remain in source
- [ ] `.env` is listed in `.gitignore` and is **not** committed
- [ ] `Dockerfile` builds cleanly: `docker build -t screetc .`
- [ ] Container starts and `/health` returns 200

## Stripe (Test mode first)

- [ ] Stripe account is in **Test mode**
- [ ] Products + Prices created; `STRIPE_PRICE_ID` (and optional Sovereign) noted
- [ ] Webhook endpoint created: `https://<your-app>.fly.dev/v1/webhook/stripe`
- [ ] Events selected: `checkout.session.completed`, `invoice.paid`, `customer.subscription.deleted`
- [ ] Webhook signing secret (`whsec_...`) copied

## Fly.io

- [ ] `fly auth login` succeeded
- [ ] App created (`fly apps create ...`) and `fly.toml` `app =` matches
- [ ] Secrets set:

  ```bash
  fly secrets set \
    STRIPE_SECRET_KEY=sk_test_... \
    STRIPE_WEBHOOK_SECRET=whsec_... \
    STRIPE_PRICE_ID=price_... \
    APP_URL=https://<your-app>.fly.dev
  ```

- [ ] `fly deploy` succeeds
- [ ] `curl https://<your-app>.fly.dev/health` → `{"status":"ok",...}`
- [ ] Landing page loads; Checkout button redirects to Stripe
- [ ] Test card `4242...` completes; success page loads
- [ ] Stripe Dashboard shows the Payment / Checkout Session
- [ ] Webhook event delivered with HTTP 200

## Optional GPU / Triton

- [ ] If using a real Triton cluster: `TRITON_CLUSTER_URL` secret set and reachable from Fly
- [ ] If not: confirm `/v1/flow` returns `"mock_inference": true` and still charges/records usage as designed

## Going live

- [ ] Switch Stripe Dashboard to **Live mode**
- [ ] Create **live** Products/Prices and a **new** live webhook endpoint
- [ ] Update Fly secrets with **live** keys only (never mix test + live)
- [ ] `fly apps restart` after secret change
- [ ] One low-value live transaction verified end-to-end
- [ ] Monitor `fly logs` and Stripe webhook delivery for 24h

## Security reminders

- [ ] No secrets in git history (`git log -p | grep -i sk_live` should be empty)
- [ ] `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` exist only as Fly secrets / local `.env`
- [ ] Frontend never receives or embeds secret keys
- [ ] Webhook rejects requests with invalid signatures (tested via Stripe “Send test webhook”)
