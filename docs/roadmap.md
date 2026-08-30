# Roadmap

## 2026-08-24 demo milestone

The professional local demo now includes Postgres/Alembic, Redis/Celery, registry-owned
dynamic forms, eight explicit simulator plugins, immutable events, demo RBAC, evidence
and KYC-lite stubs, Command Center/admin surfaces, seeded failure paths,
Prometheus/Grafana/OTel, and MailHog.

This demonstrates the target product; it does **not** complete production readiness.
Remaining work includes real identity, KMS-backed encryption, distributed abuse controls,
production object storage/scanning, disaster recovery, Spanish localization, and
one-agency-at-a-time legal and technical validation.

## Day 1 — complete local release candidate

- [x] Searchable directory of 28 official complaint destinations
- [x] Consent-first FCC intake, review, simulated submission, and receipt
- [x] Durable local tracking record and local-content deletion
- [x] Responsive, accessible UI with browser and automated axe verification
- [x] API contract, tests, containers, documentation, and repository governance

## Production readiness

- [ ] Independent legal, privacy, threat-model, and accessibility review
- [ ] Authentication and authorization for tracking and deletion
- [ ] Managed encrypted database, retention jobs, backups, and recovery tests
- [ ] Distributed abuse controls, alerting, and operational runbooks
- [ ] Signed FCC integration agreement and sandbox certification
- [ ] Staged deployment with synthetic monitoring and rollback rehearsal

## Expansion

- [ ] Spanish localization and plain-language review
- [ ] Evidence attachments with malware scanning and strict retention
- [ ] Add agencies one at a time after integration-risk review
- [ ] Optional account portal and notification preferences

No roadmap item should imply automated submission until the receiving agency's rules and connector have been verified.
