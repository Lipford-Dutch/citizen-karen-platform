# Security implementation notes

## Interactive demo controls and boundaries

- Demo JWTs represent anonymous citizen, authenticated citizen, and admin roles. They are local walkthrough identities, not production authentication.
- API responses include the non-government-service disclaimer; agency/schema responses also carry it in the body.
- Submission velocity is process-bounded, and the zero-length honeypot remains validated by the request model.
- Evidence is type/size constrained. A malware-signature stub blocks the EICAR marker and records a 30-day retention deadline; it is not a production scanner.
- Complaint deletion removes the local payload and evidence while retaining the minimal receipt and append-only deletion event.
- Metrics use bounded labels. Logs omit identity fields, complaint narratives, evidence, tokens, and request bodies.

Before any shared deployment, replace demo JWT issuance, process-local limits, local evidence storage, static Compose secrets, MailHog, and the OTel debug exporter. Validate each agency independently; no mock proves real-world compatibility.

The Day-1 application minimizes exposure by default: the FCC connector simulates submission unless network mode is explicitly enabled, CORS is allowlisted, complaint request bodies are not logged, common Social Security and payment-card patterns are rejected, and deletion redacts the stored local payload.

The production frontend adds a restrictive Content Security Policy, clickjacking protection, content-type protection, a permissions policy, and same-origin API proxying. The backend returns request IDs and security headers and exposes only aggregate Prometheus metrics.

## Release boundary

This is not yet approved for public production complaint data. Before an internet deployment, add and verify:

- authenticated access to receipts and deletion;
- managed encryption at rest and secret storage;
- distributed rate limiting, abuse monitoring, and an accessible bot defense;
- TLS termination, backups, retention enforcement, and restore exercises;
- agency-specific legal approval and a real connector contract;
- an independent penetration test and privacy review.

See the repository-level [security policy](https://github.com/Lipford-Dutch/citizen-karen-platform/blob/main/SECURITY.md) for private reporting instructions.
