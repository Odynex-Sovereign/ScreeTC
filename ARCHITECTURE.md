# Architecture — ScreeTC

**Status:** Current state (verified) + recommended production architecture for a commercially viable MVP.

---

## 1. Current Architecture (verified)

```mermaid
flowchart TB
    subgraph Client["Client"]
        Browser["Landing page / SDK"]
        APIClient["API caller with customer_stripe_id"]
    end

    subgraph Gateway["Flask API Gateway"]
        Health["/health"]
        Checkout["/v1/checkout → Stripe"]
        Flow["/v1/flow"]
        BillingMW["OdynexBillingEngine"]
        Flow --> BillingMW
        Flow --> TritonProxy["HTTP proxy to Triton URL"]
    end

    subgraph External["External / Placeholder"]
        Stripe["Stripe Checkout + Webhooks"]
        Triton["Triton Inference Server<br/>(placeholder URL or local compose)"]
    end

    Browser --> Checkout
    APIClient --> Flow
    Checkout --> Stripe
    TritonProxy --> Triton
```

**Observed gaps**
- Triton endpoint is a placeholder.
- No trained model weights in repo.
- Billing entitlement is stub / in-memory.
- Secrets appear in environment **and** in one hard-coded path (must be removed).
- No durable database, no proper auth, no audit log.

---

## 2. Target Architecture (Industrial MVP)

```mermaid
flowchart TB
    subgraph Clients
        Web["Marketing + App"]
        SDK["odynex_sdk / HTTP clients"]
    end

    subgraph Edge["API & Control Plane"]
        GW["API Gateway<br/>(FastAPI or hardened Flask)"]
        Auth["Auth + API keys + RBAC"]
        Meter["Usage metering + entitlement"]
        Audit["Immutable audit log"]
    end

    subgraph Data["Data Layer"]
        PG[(PostgreSQL)]
        Redis[(Redis<br/>rate-limit, idempotency, cache)]
        Obj["Object storage<br/>(exports, model artifacts)"]
    end

    subgraph Inference["Physics Runtime"]
        Adapter["Inference Adapter Interface"]
        Sim["Local Simulator<br/>(dev / demo)"]
        Triton["Triton / Modulus cluster<br/>(production)"]
        Adapter --> Sim
        Adapter --> Triton
    end

    subgraph Commercial["Commercial"]
        Stripe["Stripe Billing + Webhooks"]
        Portal["Customer Portal"]
        Quote["Quote / NDA / Enterprise workflow"]
    end

    subgraph Growth["Ethical Growth Center"]
        Ref["Referral & partner tracking"]
        Content["Content approval queue"]
        Email["Consent-based lifecycle email"]
        Leads["Lead routing → human CRM"]
    end

    Web --> GW
    SDK --> GW
    GW --> Auth
    GW --> Meter
    GW --> Audit
    Meter --> PG
    Auth --> PG
    Audit --> PG
    GW --> Adapter
    Meter --> Stripe
    Stripe --> Portal
    Quote --> Leads
    Growth --> Email
    Growth --> Content
```

---

## 3. Build-vs-Buy Decisions

| Capability | Decision | Rationale |
|------------|----------|-----------|
| Core PINN / physics models | Build (keep proprietary) | Core IP & TUTSA protection |
| API gateway + metering | Build on FastAPI or hardened Flask | Full control of usage events |
| Database | Buy managed Postgres | Reliability & backups |
| Auth / API keys | Build thin layer + optional enterprise SSO later | Simple for Axis Stream |
| Payments | Buy Stripe Billing + Customer Portal | Industry standard, fewer dark patterns |
| Email | Buy provider (Postmark, SES, etc.) with consent + unsubscribe | Deliverability + compliance |
| Object storage | Buy S3-compatible | Model artifacts & exports |
| Inference runtime | NVIDIA Triton / Modulus (production) + local simulator (dev) | Matches stated stack |
| CRM / e-signature | Abstraction + human-owned pipeline | Never auto-spam |

---

## 4. Security Architecture (required for MVP)

- All secrets exclusively from environment / secret manager. Fail closed if missing.
- Stripe webhook signature verification + idempotency keys.
- API keys hashed at rest; scoped and rotatable.
- Rate limiting per key and per IP.
- Tenant isolation tests for any multi-tenant path.
- Non-root containers; minimal attack surface.
- Structured audit log for entitlement changes, key issuance, and admin actions.
- Clear data-export and account-deletion flows.

---

## 5. Ethical Growth Architecture

```mermaid
flowchart LR
    subgraph Allowed
        Referral["Referral links + rewards<br/>with fraud controls"]
        Content["Draft → Review → Approve → Publish"]
        Email["Consent records + unsubscribe"]
        Leads["Lead form → human owner"]
    end

    subgraph Forbidden
        Spam["Unsolicited mass outreach"]
        Fake["Fake reviews / fake accounts"]
        Scrape["Prospect scraping"]
        Auto["Fully autonomous client acquisition"]
    end
```

Every external message or post requires an explicit human approval step by default.

---

## 6. Deployment Options

| Mode | Description |
|------|-------------|
| Multi-tenant SaaS (Axis Stream) | Shared control plane + metered inference |
| Region-isolated (Sovereign Gateway) | Dedicated or isolated tenant resources |
| Private / air-gapped (Odynex Core) | Customer-controlled deployment; quote + NDA + support contract |

Local development must work with the simulator only (no GPU required). Production GPU paths are explicit and documented.
