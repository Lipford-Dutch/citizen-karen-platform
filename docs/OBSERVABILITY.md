# Observability Guide — Citizen Karen / Karing USA

This document outlines what metrics, logs, and monitoring are collected, how to configure dashboards, alerting rules, and best practices for maintaining system health and transparency.

---

## 📊 What We Monitor & Why

### ✅ Core Metrics & Signals

The local demo provisions the `Citizen Karen Platform Overview` dashboard automatically.
FastAPI and SQLAlchemy emit OTel traces to the local Collector debug exporter; Prometheus
scrapes bounded-cardinality HTTP, agency, task, queue, and evidence-scan metrics. No
tracking ID, identity field, complaint narrative, evidence name, or token is a metric label.

| Signal Type | Metric / Data | Purpose |
|-------------|---------------|---------|
| Traffic / Load | `http_requests_total` (rate) | Monitor API usage, submission volume, load spikes |
| Latency / Performance | `http_request_duration_seconds_bucket` → p50/p95/p99 quantiles | Ensure compliance to latency goals (e.g. p95 < 500ms), detect performance regressions |
| Error Rate / Failures | Non-2xx status codes, backend exceptions, failed job counts (`celery_task_failed_total`) | Detect failures, bugs, upstream module issues |
| Queue / Job System | `celery_task_received_total`, retry rate, backlog size | Monitor background job health, backlog, delays, retries |
| Upstream Module Health | Success/failure rates per agency plugin, latency per submission | Identify flaky or broken agency integrations early |
| System Health / Resources | Up / liveness probes for DB, Redis, Worker; memory/CPU usage; uptime | Ensure infrastructure stability & reliability |
| Logging & Audit Trail | Structured JSON logs per request / submission / module action | For debugging, compliance, auditability, traceability |

---

## 📄 Logging & Traceability

- **Structured Logs** (JSON): Every request, background job, module submission, and status update logs metadata (timestamp, component, submission ID, module name, status, error codes)  
- **PII Safety**: Sensitive user data (names, emails, SSNs, complaint details) are stored in DB only; logs exclude or redact PII  
- **Trace IDs / Correlation IDs**: Use unique request ID per user submission — propagate throughout async job pipeline for traceability (frontend → API → queue → module → status)  
- **Optional Distributed Tracing**: Integrate OpenTelemetry (OTel) or similar tracing to visualize full execution path (frontend, API, worker, module) — helpful for debugging or performance bottlenecks  

---

## 🛠️ Dashboards & Alerting — Setup & Best Practices

### Recommended Dashboards

1. **System Overview** — request rate, latency, error rates, background job rates, queue backlog, upstream success/failure metrics  
2. **Errors & Logs** — real-time error rates + log view (requires log ingestion via Loki or similar)  
3. **Trends & Volume** — historical usage, daily/weekly complaint volume, module submissions, retry/failure trends  
4. **SLA / Reliability & Alerting** — monitors p95 latency, error thresholds, job failures, upstream reliability, queue health  

### Sample Alerting Rules

- p95 latency > 500 ms for 5+ minutes  
- Error rate > configurable threshold (e.g. 1% of requests)  
- Celery retry rate spikes or frequent job failures  
- Queue backlog above threshold (jobs pending for too long)  
- Upstream module failures exceeding threshold (e.g. 5 failures/hour for a given agency)  
- Redis / DB unreachable, liveness check fails  

Alerts should notify developers/admins (email, Slack, etc.) and optionally trigger auto‑pause / degraded mode if critical (e.g. DB down, broker down)  

---

## 📚 Setup Instructions (Initial & Onboarding)

1. Expose `/metrics` (Prometheus format) and `/healthz` endpoints in FastAPI backend (and optionally worker).  
2. Deploy Prometheus (self‑hosted or hosted) and configure scraping of all services (API, worker, Redis, DB, etc.).  
3. Configure remote‑write to hosted observability service (e.g. Grafana Cloud) or use self-hosted Prometheus + Grafana.  
4. Integrate log shipping: use structured JSON logs + ship to log store (e.g. Grafana Loki, ELK, Splunk), ensure PII is excluded / masked.  
5. Build dashboards (import JSON or build based on recommended panels), set up alert rules and contact points (email, Slack, webhook).  
6. Onboard new agency modules: ensure module instrumentation (success/failure counters, latency histograms) and include module‑specific metrics (e.g. submissions per agency).  

---

## ✅ Observability Hygiene & Best Practices

- Use consistent metric naming across modules (e.g. `agency_submission_total{agency="IRS"}`) — helps in aggregation and dashboarding.  
- Tag metrics with labels: agency name, module version, region (if multi‑region), status, error code/class.  
- Keep dashboards focussed — avoid over‑crowding; each dashboard should serve a clear purpose.  
- Document alert thresholds and alerting procedures (who responds, what to do, escalation policy).  
- Periodically audit logs & metrics to ensure no PII leakage, no unbounded log growth, and storage cost control.  
- Version your observability configs (dashboards, alert rules) in repo — treat as code.  

