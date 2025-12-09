# Agency Risk Assessment & Scoring — Karing USA

Each agency module gets a risk score — helps prioritize monitoring, testing cadence, and fallback procedures.

## 🚦 Risk Factors & Scoring

| Factor | Weighting | What to Evaluate |
|--------|-----------|-----------------|
| Change Frequency | High | How often does the agency change form/API/portal? |
| Automation Difficulty | Medium | CAPTCHA, dynamic JS, multi-step forms, PDF + e‑signature required? |
| Data Sensitivity | High | Does it accept SSN, DOB, financial data, identity‑sensitive info? |
| Response Stability | Medium | Does the agency API/portal respond reliably? (uptime, rate limits) |
| Legal / Compliance Risk | High | Privacy laws, PII storage, user consent requirements, compliance burden |
| Volume Expectation | Medium | Estimated submission volume — affects performance/rate limit considerations |
| Abuse Risk | Medium | Risk of spam, malicious submissions, fraud (e.g. identity theft reports) |

---

## 📊 Sample Risk Score Template (per agency)

