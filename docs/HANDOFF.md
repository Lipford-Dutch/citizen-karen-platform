# Release handoff

## Delivered scope — 1.0.0-rc.2 full-scale local demo

The release candidate now provides the full interactive vision demo while retaining the original FCC flow and 28-destination directory. The Command Center, dynamic schema-driven intake, Postgres source-of-truth, immutable events, Celery retry/escalation, demo RBAC, evidence controls, observability stack, email capture, and admin walkthrough all run locally from one Compose command.

## Runtime modes

- `simulate` (default outside Compose): synchronous, local connectors with no network transmission.
- `network` (Compose FCC only): sends to the repository's mock FCC service.
- Every non-FCC plugin is a high-fidelity local mock. Failure Lab deterministically demonstrates success, retry, permanent failure, and escalation.
- No production government endpoint or credential is included.

## Verification baseline

- Backend: Ruff, mypy, 34 pytest tests, and 94% statement coverage.
- Frontend: ESLint, 7 Vitest tests, jest-axe, TypeScript production build, and high-severity npm audit gate.
- Browser: desktop and 390 px mobile directory, filing, review, receipt, status, navigation, and deletion-confirmation paths.
- Packaging: Compose configuration plus frontend, backend, and mock-agency images.

Run every command in the root README before a release. GitHub Actions intentionally run only after merge to `main` or by manual dispatch, keeping development branches dormant.

The public showcase is built from the screenshot-led custom MkDocs homepage at <https://lipford-dutch.github.io/citizen-karen-platform/>. The Pages workflow publishes only after the release PR lands on `main`.

## Honest production blockers

Demo JWTs are intentionally self-issued, rate limiting is process-local, evidence scanning is a signature stub, local volumes are not KMS-encrypted, email is captured by MailHog, OTel uses a debug exporter, and no real government submission has been validated. Postgres and Redis improve architectural fidelity; they do not make this production-ready. See [Security](SECURITY.md) and the [demo runbook](DEMO_RUNBOOK.md).
