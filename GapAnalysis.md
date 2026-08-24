# Release gap analysis

| Area | Implemented now | Remaining before public production |
| --- | --- | --- |
| Consent and transparency | Required versioned consent, review step, clear forwarding disclosure, consent event, status receipt | Counsel-approved terms and jurisdiction review |
| Data minimization | Narrow intake, no evidence upload, PII-safe logs, sensitive-number rejection, payload deletion | Authenticated access, retention automation, managed encryption |
| Abuse prevention | Hidden honeypot, payload limits, strict schemas | Distributed rate limits and accessible bot challenge |
| Accessibility | Semantic React UI, visible focus, reduced motion, responsive layout, automated axe tests | Independent WCAG 2.2 AA audit and assistive-technology matrix |
| Agency automation | FCC-only connector boundary, offline simulation, Docker mock, explicit official-site fallbacks | Signed real FCC contract, sandbox certification, production failure playbook |
| Operations | Health endpoint, request IDs, JSON logs, metrics, containers, 90% CI coverage floor | Hosted monitoring, alert routing, backups, recovery and incident exercises |
| User control | Tracking receipt and local payload deletion | Identity verification, access export, agency-side deletion instructions |
| Localization | English plain-language release | Spanish localization and content review |

The local Day-1 implementation is complete. The items in the final column are release gates for handling real public complaint data, not optional polish.
