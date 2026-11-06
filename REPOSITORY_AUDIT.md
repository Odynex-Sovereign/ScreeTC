# Repository Audit — ScreeTC

**Audit date:** 2026-11-06  
**Repository:** https://github.com/Odynex-Sovereign/ScreeTC  
**Company:** Odynex Axis Logistics LLC  
**Founder / Institutional Architect:** David Fabian Cadelinia  
**Contact:** david@odynexaxis.biz | +1 229-364-1658 | https://www.odynexaxis.biz  
**Affiliation note:** NVIDIA Inception Program Member (as stated by founder)

This document distinguishes **verified repository facts** from **assumptions**.

---

## 1. Verified Repository Facts

| Item | Value |
|------|-------|
| Stated product | Real-time Physics-Telemetry Infrastructure-as-a-Service (IaaS) |
| Core claim | Virtualize fluid dynamics / thermal flows into low-latency cloud APIs via Physics-Informed Neural Networks (PINNs), NVIDIA Modulus, and Triton Inference Server |
| Primary language | Python (Flask) |
| Key dependencies | flask, stripe, numpy, requests, gunicorn |
| Deployment targets | Docker, docker-compose, Fly.io (A10G GPU), Triton container |
| License posture | Proprietary / TUTSA trade-secret claims + NDA.md; not open-source |
| Stars / forks | 0 / 0 |
| Approximate commits | ~47 |

### Intended commercial model (from README)

| Tier | Deployment | Target | Pricing (as written) |
|------|------------|--------|----------------------|
| Axis Stream | Multi-tenant public API | Indie developers, UAV operators | $0.005 per API / telemetry frame |
| Sovereign Gateway | Region-isolated clusters | Municipalities, regional logistics | $4,500 / month base |
| Odynex Core | Air-gapped private appliance | Aerospace, defense, F1 / automotive | Custom enterprise contract |

### Actual file tree (verified)

```
.
├── .github/workflows/          # deploy, google, ibm, jekyll-docker
├── models/screetc_pinn/        # config.pbtxt only (no weights)
├── public/                     # index.html, success.html
├── src/                        # duplicates of root Python modules
├── billing_middleware.py
├── create_stripe_catalog.py
├── main_api_gateway.py         # Flask API + Stripe Checkout
├── odynex_sdk.py
├── index.html / success.html
├── Dockerfile, docker-compose.yml, fly.toml, nginx.conf
├── NDA.md, LICENSE, PRE_DEPLOY_CHECKLIST.md, README-DEPLOY.md
└── requirements.txt
```

### Current functionality that exists

- Flask API gateway with `/health`, static landing page, Stripe Checkout session creation (`/v1/checkout`), and a `/v1/flow` physics-telemetry endpoint.
- Billing middleware class (`OdynexBillingEngine`) that checks entitlement and can meter usage.
- Stripe catalog helper script.
- Landing page + success page (public/).
- Docker multi-stage build and Fly.io config targeting NVIDIA A10G.
- docker-compose that launches a Triton Inference Server container + nginx gateway.
- Strong legal framing (TUTSA, GATS Mode 1/3, NDA).

### Broken, incomplete, or non-production-ready

- **No trained PINN weights** are present in the public repository. Only a Triton `config.pbtxt` skeleton exists.
- Triton URL in code is a placeholder (`YOUR_NVIDIA_GPU_SERVER_IP` or localhost).
- One code path contains a hard-coded placeholder Stripe secret (`sk_live_odynex_axis_logistics_secret`) — **critical security defect**.
- Payload construction in `/v1/flow` has incomplete / invalid JSON shape fields in the inspected source.
- Entitlement verification is in-memory / stub-level; no durable customer or usage ledger.
- No authentication beyond a customer_stripe_id string check.
- No rate limiting, audit log, or tenant isolation tests.
- No automated tests of any kind visible.
- Public landing page is static HTML; no real product demo that runs without a live GPU cluster and valid Stripe keys.
- Duplicate root / `src/` modules create maintenance risk.

### Security risks (verified)

1. Hard-coded or placeholder live-looking Stripe secret in source.
2. No webhook signature verification path fully hardened in all copies.
3. No secrets management pattern beyond `os.environ`.
4. Docker / Fly configs assume GPU access; misconfiguration can expose inference ports.
5. Trade-secret claims are strong; any public demo must carefully avoid leaking proprietary coefficients or weights.

### Missing pieces for a commercially viable, ethically growth-enabled product

- Durable identity, organization, and subscription model (Postgres + proper auth).
- Real model artifact management and versioning.
- Usage metering that is accurate, auditable, and dispute-ready.
- Customer portal, invoices, failed-payment handling, cancellation, and data export.
- Observability (structured logs, metrics, tracing, error tracking).
- Ethical Growth Center (referral, content approval workflow, consent-based email, lead routing) — **none of which may auto-send outreach**.
- Comprehensive test suite and CI that actually runs the critical paths.
- Clear “human approval required” gate for any external publishing or outreach.

---

## 2. Assumptions (explicitly labeled)

- Private or customer-side deployments may contain trained weights and production Triton endpoints not present in this public tree.
- The founder intends ScreeTC to become a revenue-generating physics utility layer for industrial and logistics customers.
- “Autonomous 24/7 client acquisition” is **not** a capability that can or should be claimed; any growth system must remain consent-based and human-approved.

---

## 3. Recommended remediation priorities

1. **Immediate:** Remove every hard-coded secret. Enforce environment-only configuration and fail closed if Stripe / Triton URLs are missing.
2. Replace placeholder Triton calls with a local simulator for development + a real adapter interface for production.
3. Introduce a proper data model (customers, subscriptions, usage events, audit log) with Postgres.
4. Harden Stripe webhooks with signature verification + idempotency.
5. Build a minimal but complete self-serve path: landing → checkout → success → API key issuance → metered `/v1/flow`.
6. Add an internal Growth Center that supports ethical channels only (referral links, approved content, consent-based lifecycle email, sales lead routing with human review).
7. Never promise or implement unsolicited mass outreach, fake social activity, or automated client acquisition.

---

## 4. Summary judgment

ScreeTC is a **promising commercial direction** (real-time physics telemetry API for industrial use cases) with a working Stripe checkout skeleton and deployment scaffolding. It is **not yet a production-ready, self-sustaining product**. The path to revenue is a focused industrial MVP with honest metering, solid security, and ethical growth systems — not autonomous spam or claims that the software “gets clients by itself.”
