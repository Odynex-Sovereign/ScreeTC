# Product Requirements — ScreeTC

**Company:** Odynex Axis Logistics LLC  
**Founder & Institutional Architect:** David Fabian Cadelinia  
**Contact:** david@odynexaxis.biz · +1 229-364-1658 · https://www.odynexaxis.biz  
**Note:** NVIDIA Inception Program Member (founder-stated)

---

## 1. Product Mission

ScreeTC turns slow, offline fluid-dynamics and thermal simulations into a low-latency, metered cloud API that industrial and logistics customers can call at runtime. It aims to become a physics utility layer for autonomous fleets, green data centers, advanced manufacturing, and related domains.

One-sentence value:  
**Call a simple API and receive real-time (or near-real-time) flow and thermal field predictions instead of waiting hours for traditional CFD.**

---

## 2. Primary Users & Jobs-to-be-Done

| Segment | Primary job |
|---------|-------------|
| UAV / drone operators & fleet managers | Predict aerodynamic loads and thermal effects in changing conditions |
| Data-center & facility operators | Estimate thermal plumes and cooling effectiveness |
| Advanced manufacturing / process engineers | Runtime fluid / thermal awareness on the factory floor |
| Municipal / regional logistics teams | Region-isolated physics services under data-sovereignty constraints |
| Aerospace & high-performance automotive (later) | Air-gapped or private-appliance deployments |

**Jobs-to-be-done**
- Submit domain points + boundary conditions and receive vector / pressure / temperature fields.
- Meter usage accurately and pay only for what is consumed (Axis Stream) or via flat / custom contracts.
- Deploy in multi-tenant cloud, region-isolated, or fully private / air-gapped modes.
- Obtain commercial terms, NDA, and support through a clear human path.

---

## 3. Value Propositions

- Runtime physics instead of overnight batch jobs.
- Metered, transparent pricing for the entry tier.
- Clear path from self-serve API to private / sovereign deployments.
- Strong IP posture (TUTSA + NDA) that sophisticated buyers expect.
- Built for NVIDIA accelerated infrastructure (Modulus / Triton path).

---

## 4. User Roles (target)

- Individual developer / operator (Axis Stream)
- Organization admin / billing admin (Sovereign Gateway & above)
- Internal staff / support / super-admin (Odynex)
- Enterprise procurement / security reviewer (Odynex Core)

---

## 5. Core Workflows (MVP)

1. Discover product via marketing site or partner referral.
2. Create account / start Stripe Checkout for Axis Stream or request Sovereign / Core quote.
3. Receive API credentials after successful payment or contract activation.
4. Call `/v1/flow` (or successor) with domain points and fluid parameters.
5. Receive predicted fields; usage is metered and appears on invoice / portal.
6. Manage billing, download invoices, export data, or cancel via customer portal.
7. (Enterprise) Sign NDA → technical evaluation → custom contract → private deployment.

---

## 6. Non-Goals

- Autonomous or unsolicited outreach that contacts people without consent.
- Fake reviews, fake social accounts, scraping of competitor or prospect lists.
- Claims that the software “automatically gains clients” or “markets itself 24/7 without human involvement.”
- Medical, clinical, or safety-critical certification claims without independent validation.
- Open-sourcing of trained proprietary weights or core IP.

---

## 7. Ethical Growth Requirements (mandatory)

Any growth system built for ScreeTC must:

- Require **explicit human approval** before any external message, post, or campaign is published.
- Support only consent-based email (welcome, activation, education, renewal, win-back) with clear unsubscribe and consent records.
- Provide referral links and transparent affiliate / partner tracking with fraud controls.
- Route sales leads to a human pipeline; never auto-spam.
- Log every external action for audit.
- Include rate limits and anti-abuse controls.

The product may improve discovery, conversion, retention, and partner-led growth. It may **not** promise or implement fully autonomous client acquisition.

---

## 8. Measurable KPIs

| Area | KPI |
|------|-----|
| Product | API success rate, p95 latency, metering accuracy |
| Commercial | Paid conversion rate, MRR / ARR, churn, expansion revenue |
| Trust | Time-to-first-successful-call, support ticket volume, NDA-to-contract cycle time |
| Growth (ethical) | Referral conversion, content approval queue health, consent opt-in rate, partner-sourced pipeline |

---

## 9. Contact & Commercial Path

All commercial, licensing, and partnership inquiries:

**David Fabian Cadelinia**  
Founder & Institutional Architect  
Odynex Axis Logistics LLC  
Email: david@odynexaxis.biz  
Phone: +1 229-364-1658  
Web: https://www.odynexaxis.biz  

Enterprise / private-deployment / NDA requests should be routed through a documented lead form that captures organization, use case, seat / volume estimates, compliance needs, and procurement timeline, then handed to a human owner.
