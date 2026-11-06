# Roadmap — ScreeTC

**Guiding principle:** Smallest credible paid product first. Ethical growth only. No claims of autonomous client acquisition.

**Commercial contact:** David Fabian Cadelinia · david@odynexaxis.biz · +1 229-364-1658 · https://www.odynexaxis.biz

---

## Milestone 0 — Security & honesty (1 week)

**Must-fix**
- Remove every hard-coded secret (especially any Stripe key).
- Fail closed if `STRIPE_SECRET_KEY`, webhook secret, or Triton URL are missing in production.
- Replace broken / incomplete JSON payload construction with validated, typed requests.
- Document clearly that public repo contains no trained weights; production inference requires a configured cluster or private artifacts.

**Acceptance:** No secrets in source; local `docker compose` + simulator runs without GPU; CI passes lint + basic import checks.

---

## Milestone 1 — Credible self-serve MVP (6–8 weeks)

**Goal:** A developer can pay, receive an API key, call a working (simulated or real) physics endpoint, and see usage on a portal.

**Acceptance criteria**
- Durable Postgres schema: users, organizations, API keys, subscriptions, usage events, audit log.
- Stripe Checkout + Customer Portal + verified webhooks + failed-payment handling.
- Axis Stream metered path with accurate unit accounting ($0.005 / frame or configurable).
- Local simulator that returns deterministic fictional fields so demos work without GPU.
- Production adapter interface that can point at a real Triton / Modulus endpoint when credentials and model artifacts are present.
- Landing page, pricing page, success page, basic docs, health checks.
- API key issuance after successful payment; key rotation and revocation.
- Data export and account deletion flow.
- Unit + integration tests for billing, metering, and the core `/v1/flow` path.
- `.env.example` fully documented; Docker Compose for local full stack.

**Out of scope for MVP:** Autonomous outreach, children’s products, multi-tenant education portals, Nasdaq/Siemens deep integrations.

---

## Milestone 2 — Ethical Growth Center + Sovereign tier (4–6 weeks after MVP)

**Acceptance criteria**
- Referral links with fraud controls and transparent rewards.
- Content drafting → human approval → scheduled publish workflow.
- Consent-based lifecycle email (welcome, activation, education, renewal, win-back) with unsubscribe and consent records.
- Lead capture form that routes to a human owner (CRM abstraction).
- Conversion and retention dashboards for internal use only.
- Sovereign Gateway path: higher base fee, region isolation notes, quote workflow.
- NPS / CSAT and churn survey with human review of feedback.

---

## Milestone 3 — Enterprise / Private (quote-driven)

**Acceptance criteria**
- NDA + technical evaluation workflow.
- Quote request form capturing organization, use case, volume, compliance needs, procurement timeline.
- Documented private / air-gapped deployment options and support boundaries.
- Optional SSO / advanced RBAC for higher tiers.
- Clear comparison page: subscription vs private deployment vs white-label / licensing (all quote-based for the latter).

**Never** publish a self-serve “buyout” price for source code or full IP without legal and executive review.

---

## Later phases

- Real model-artifact management and versioning.
- Additional physics domains only when validated.
- Partner marketplace and certified integrator program (human-vetted).
- Optional education materials that teach the *concepts* of PINNs and runtime physics — in a separate, age-appropriate product if desired.

---

## Success metrics by milestone

| Milestone | Primary success signal |
|-----------|------------------------|
| 0 | Zero secrets in repo; simulator runs locally |
| 1 | First real paid Axis Stream customer completes a successful metered call |
| 2 | Measurable referral or partner-sourced pipeline; zero unsolicited outreach incidents |
| 3 | First signed Sovereign or Core contract with clear support boundaries |
