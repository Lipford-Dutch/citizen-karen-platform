# Full-scale interactive demo runbook

Citizen Karen is not a government service or legal advice. All agency interactions in this runbook are simulated; the only network connector targets the repository's local FCC mock.

## Start and verify

```bash
docker compose -f infra/docker-compose.yml up --build
docker compose -f infra/docker-compose.yml ps
```

Wait until `frontend`, `backend`, `postgres`, `redis`, `worker`, `prometheus`, `grafana`, `mailhog`, and `mock-fcc` are healthy and `seed` exits successfully.

## Stakeholder walkthrough

1. Open the Command Center at <http://localhost:8080>. Point out synthetic cases, explicit status text, next actions, and the persistent non-government disclaimer.
2. Open **Find an agency**. Compare an official external destination with a labeled demo plugin and its risk score.
3. Open **File a complaint**, select Failure Lab, and demonstrate `Success path`, `Retry path`, `Permanent failure`, or `Escalation path`. Review the plugin-provided schema and explicit consent record before submission.
4. On a case, open the immutable audit trail, attach a small synthetic text or image file, and explain the malware-scan and 30-day retention stubs.
5. Open **Admin demo**, then Grafana, MailHog, and OpenAPI. No case content or citizen PII appears in metrics or structured logs.
6. Delete the local case copy. Complaint content and local evidence are removed; the audit event and minimal receipt remain.

## Deterministic demo identities

- Citizen: `demo-citizen` / Karen Citizen
- Admin: `demo-admin` / Alex Administrator
- Anonymous: no account, submission and tracking only

The UI obtains short-lived local demo JWTs without passwords while `DEMO_MODE=true`. Disable demo mode and replace JWT issuance before any shared deployment.

## Reset

```bash
docker compose -f infra/docker-compose.yml down --volumes
```

This permanently removes the local demo's Postgres, Redis, Prometheus, and Grafana volumes.
