# Citizen Karen 1.0.0-rc.2

Released: 2026-08-30

Citizen Karen 1.0.0-rc.2 is the first full-scale, stakeholder-ready local demonstration of the platform vision. It is an independent civic-tech prototype, not a government service or legal advice. Every agency interaction is simulated unless a screen explicitly links the user to an official external destination.

## Release highlights

- One-command environment with Postgres, Redis, Celery worker and scheduler, Prometheus, Grafana, MailHog, OpenTelemetry Collector, frontend, backend, seed job, and mock FCC service.
- Eight registry-owned plugins: FCC plus explicit IRS, FTC, EPA, CFPB, State DMV, Benefits, and Failure Lab simulations.
- Dynamic guided forms generated from plugin schemas with review and explicit recorded consent.
- Citizen Command Center with seeded cases, next actions, reminders, immutable timelines, retry, failure, and escalation states.
- Evidence upload and retention demonstrations with a deliberately limited malware-scan stub.
- Demo citizen, anonymous, and administrator roles with clear production replacement boundaries.
- Screenshot-led GitHub Pages showcase and expanded release, security, observability, accessibility, and operational documentation.

## Ten-minute showcase

1. Start the stack with `docker compose -f infra/docker-compose.yml up --build`.
2. Open <http://localhost:8080> and review the eight synthetic cases in the Command Center.
3. Compare an official directory destination with a simulated plugin entry and its risk declaration.
4. File through Failure Lab to demonstrate success, retry, permanent failure, or escalation.
5. Inspect the case audit trail, attach synthetic evidence, and review retention and deletion controls.
6. Open Grafana, MailHog, Prometheus, and OpenAPI to show the observability-first architecture.

The complete script, service URLs, identities, and reset procedure are in the [demo runbook](DEMO_RUNBOOK.md).

## Verified quality baseline

- Backend Ruff, formatting, mypy, and 34 pytest tests with more than 90% statement coverage.
- Frontend ESLint, seven Vitest tests, jest-axe checks, TypeScript production build, and high-severity npm audit gate.
- Strict MkDocs build, Docker Compose configuration validation, desktop and mobile browser checks, and screenshot interaction verification.

## Known production blockers

This release is not approved for production complaint data. Demo JWTs are self-issued, rate limiting is process-local, evidence scanning is a signature stub, local volumes are not KMS-encrypted, email is captured locally, and no production government transmission has been certified. See [Security](SECURITY.md), [Data governance](DATA_GOVERNANCE.md), and [Legal boundaries](LEGAL_BOUNDARIES.md).

## Upgrade and reset

This is a local release candidate. To obtain a pristine demonstration dataset:

```bash
docker compose -f infra/docker-compose.yml down --volumes
docker compose -f infra/docker-compose.yml up --build
```

The first command permanently deletes only the local Compose volumes for this demo.
