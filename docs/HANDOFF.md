# Release handoff

## Delivered scope

The release candidate provides a complete local path from destination discovery through FCC complaint review, consent, submission simulation, tracking, and local-content deletion. The directory contains 28 unique official destinations sourced from the repository workbook and research notes.

## Runtime modes

- `simulate` (default outside Compose): generates a realistic local FCC reference without network transmission.
- `network` (Compose): sends to the repository's mock FCC service.
- No production FCC endpoint or credential is included.

## Verification baseline

- Backend: Ruff lint and format, 22 pytest tests, 95% statement coverage.
- Frontend: ESLint, 7 Vitest tests, jest-axe, TypeScript production build, and zero high-severity npm audit findings.
- Browser: desktop and 390 px mobile directory, filing, review, receipt, status, navigation, and deletion-confirmation paths.
- Packaging: Compose configuration plus frontend, backend, and mock-agency images.

Run every command in the root README before a release. GitHub Actions intentionally run only after merge to `main` or by manual dispatch, keeping development branches dormant.

## Known production blockers

The prototype does not authenticate tracking IDs, encrypt SQLite at the application layer, rate-limit across instances, or submit to a real FCC API. These are explicit production blockers, not silent assumptions. See [Security](SECURITY.md) and the [roadmap](roadmap.md).
