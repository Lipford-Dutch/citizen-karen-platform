# Changelog

All notable changes to this project are documented here.

## 1.0.0-rc.3 — 2026-08-30

### Security

- Updated PyJWT to 2.13.0 to address algorithm-confusion, JWK, SSRF, and denial-of-service advisories.
- Updated python-multipart to 0.0.31 to address multipart parsing, parameter smuggling, and denial-of-service advisories.

### Verification

- Re-ran backend linting, formatting, typing, tests, and the 90% coverage gate.
- Re-generated the OpenAPI 3.1 contract and re-validated the strict documentation build.

## 1.0.0-rc.2 — 2026-08-30

- Upgraded the demo source of truth to Alembic-managed Postgres with immutable state-transition events.
- Added Redis and Celery submission, polling, exponential retry, escalation, and scheduled retention workflows.
- Expanded the plugin registry to eight explicitly simulated integrations with registry-owned dynamic forms and risk declarations.
- Added demo roles, evidence handling and scan stubs, rate and velocity controls, KYC-lite declarations, and confirmation-email capture.
- Added the Citizen Command Center, admin walkthrough, enhanced directory, case evidence, and audit-trail experiences.
- Added Prometheus, Grafana, OpenTelemetry, MailHog, deterministic seed data, and health/readiness gates to the one-command Compose stack.
- Published a screenshot-led GitHub Pages showcase, refreshed repository governance and community surfaces, and consolidated Pages deployment.
- Raised backend coverage above 90%, retained automated accessibility checks, and documented honest production blockers.

## 1.0.0-rc.1 — 2026-08-24

- Rebuilt the frontend as a responsive React and TypeScript civic wayfinding experience.
- Added the 28-destination official complaint directory and complete FCC filing path.
- Added consent validation, durable tracking receipts, agency references, and local-copy deletion.
- Added FastAPI schemas, security headers, structured logging, metrics, and comprehensive tests.
- Added production containers, reverse proxy, current OpenAPI contract, repository governance, and release documentation.
- Consolidated GitHub Actions into post-merge verification to keep development branches dormant.
