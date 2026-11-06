# Design System — ScreeTC

**Brand owner:** Odynex Axis Logistics LLC  
**Founder contact (for commercial & institutional inquiries):**  
David Fabian Cadelinia · david@odynexaxis.biz · +1 229-364-1658 · https://www.odynexaxis.biz

---

## 1. Brand positioning

**Positioning**  
Real-time physics utility for industrial and logistics systems — fluid and thermal fields on demand via secure, metered APIs.

**Personality**  
Precise · Technical · Trustworthy · Calm · Sovereign  

**Avoid**
- Consumer “AI magic” hype  
- Claims of autonomous client acquisition or 24/7 self-marketing without human oversight  
- Medical or safety-critical certification language without independent validation  
- Playful or child-oriented visuals  

---

## 2. Voice & tone

- Short, concrete, evidence-based sentences.  
- Admit limitations (simulation vs production weights, public vs private artifacts).  
- Pricing and limits are stated clearly; no dark patterns.  
- Commercial and licensing language is formal and direct; point to human contact for enterprise.

Good example:  
> “Axis Stream meters usage at $0.005 per telemetry frame. You can view invoices and cancel in the customer portal at any time.”

Bad example:  
> “ScreeTC will automatically find and close clients for you around the clock.”

---

## 3. Visual foundations

### Color tokens (industrial, high-trust)

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--bg-primary` | `#F8FAFC` | `#0B1220` | Page background |
| `--bg-surface` | `#FFFFFF` | `#111827` | Cards, panels |
| `--text-primary` | `#0F172A` | `#F1F5F9` | Body |
| `--text-secondary` | `#475569` | `#94A3B8` | Secondary |
| `--accent` | `#0F4C81` | `#3B82F6` | Primary actions |
| `--success` | `#166534` | `#22C55E` | Positive |
| `--warning` | `#92400E` | `#F59E0B` | Caution |
| `--danger` | `#991B1B` | `#EF4444` | Errors, billing blocks |
| `--border` | `#E2E8F0` | `#1F2937` | Dividers |

WCAG 2.2 AA contrast is mandatory for all text and interactive elements.

### Typography

- System or industrial open fonts (Inter, IBM Plex Sans, or equivalent).  
- Body ≥ 16 px / 1.5 line-height.  
- Monospace for API keys, latency numbers, and code.  

### Spacing & layout

- 4 px base unit.  
- Engineering-dashboard density; generous padding on marketing pages.  
- Clear hierarchy: product claim → proof → pricing → human contact.

---

## 4. Component principles

- **Empty states:** Explain what is missing and the single next action.  
- **Error states:** Non-blaming, actionable; never hide billing or entitlement failures.  
- **Forms:** Explicit labels, client + server validation, no pre-checked marketing boxes.  
- **Pricing cards:** Show monthly and annual, exact limits, and what happens on overage or cancellation.  
- **Contact blocks:** Always include the founder / company contact for institutional inquiries.

---

## 5. Accessibility

**Target:** WCAG 2.2 AA  

Required from the first interactive surface:
- Keyboard-only operation and visible focus  
- Screen-reader labels  
- Sufficient contrast  
- Clear language; define technical terms on first use  

---

## 6. Information architecture (marketing + app)

```
/                     → Product overview + primary CTA
/pricing              → Transparent tiers + “Request enterprise quote”
/docs                 → Quick start, API reference, limits
/security             → Trust, data handling, compliance posture
/contact              → Lead form + direct founder contact
/success              → Post-checkout confirmation
/dashboard            → (authenticated) keys, usage, billing portal link
/growth               → (internal) Ethical Growth Center
```

Footer and contact pages must surface:

**David Fabian Cadelinia**  
Founder & Institutional Architect  
Odynex Axis Logistics LLC  
david@odynexaxis.biz · +1 229-364-1658 · www.odynexaxis.biz

---

## 7. Explicit non-goals for design

- Any surface that targets minors as primary users.  
- Social feeds or public discoverability of customer projects by default.  
- Dark patterns around upgrades, cancellation, or data collection.  
- Visual language that implies the product runs fully autonomous sales or outreach.
