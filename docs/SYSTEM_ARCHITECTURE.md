# System Architecture — Citizen Karen / Karing USA

## Full-scale local demo topology (1.0.0-rc.3)

```text
Browser → nginx SPA/reverse proxy → FastAPI → Postgres source of truth
                                      ├──→ Redis → Celery worker/scheduler
                                      │              └──→ plugin registry
                                      ├──→ MailHog
                                      └──→ Prometheus + OTel → Grafana
```

The plugin manifest is the only capability catalog. It owns dynamic form schema,
risk/KYC metadata, automation boundaries, official URL, submission, polling, and
escalation behavior. API routes do not contain agency-specific form logic.

Compose uses Alembic-managed Postgres. SQLite remains an isolated development and
test fallback behind the same repository interface; it is not the demo source of truth.

## 🎯 Purpose

This document describes the overall architecture of the Citizen Karen platform: core components, data flow, module/plugin framework, and infrastructure considerations.

---

## 📦 High-Level Components

| Layer / Component | Responsibility |
|------------------|----------------|
| **Frontend (Citizen UI + Admin UI)** | React-based SPA (or Next.js) for users to submit requests, track status, and for admins to monitor queue, retry failures, view dashboards. |
| **API Gateway / Backend API** | FastAPI server exposing REST and GraphQL endpoints; handles request validation, tracking ID generation, status queries. |
| **Orchestrator & Submission Engine** | Accepts validated citizen‑friendly payloads, selects the appropriate upstream “agency module,” transforms payload to agency‑specific schema, queues submission job. |
| **Plugin / Module Framework** | Each agency connector lives as a module/plugin, implementing a standard interface: validate → submit → check status → escalate. Modules are containerized / modular for easy onboarding. |
| **Background Job Queue** | Redis (broker) + Celery (worker) or equivalent; handles asynchronous submission, retries, backoff, status polling, escalation workflows. |
| **Persistent Data Store (SOT DB)** | PostgreSQL (or other relational DB) storing all citizen submissions (Source-of-Truth), metadata, submission history, status, audit trail. |
| **Observability & Monitoring** | Prometheus metrics, structured logging, optional tracing (OTel), dashboarding (Grafana, Loki, etc.), alerting for failures, health‑checks. |
| **Infrastructure / Orchestration** | Docker (for dev), Kubernetes (for prod), configuration via environment variables / secrets, support for scaling, high availability, container orchestration. |
| **Security & Compliance Layer** | Encryption for PII, secure secrets handling, access controls, audit logs, data retention policies, rate limiting / abuse protection. |

---

## 🔄 Data Flow & Workflow — End to End

