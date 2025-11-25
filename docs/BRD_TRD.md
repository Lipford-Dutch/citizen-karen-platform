Citizen Karen - Business & Technical Requirements
Business Requirements

Allow citizens to submit complaints without knowing the target agency.

Auto-route complaints to the correct agency connector.

Provide immediate tracking IDs for all submissions.

Persist all complaints and support status retrieval.

Handle upstream agency outages gracefully.

Provide an accessible, responsive UI (WCAG AA).

Support modular onboarding of 50+ agencies via plugins.

Technical Requirements

FastAPI backend, React frontend.

Plugin-based agency integration framework.

JSON/REST API with OpenAPI 3.1 spec.

PostgreSQL data store with audit trail.

Structured logging, Prometheus metrics, health checks.

Retry and backoff for upstream calls.

Containerized deployment with Docker.

Non-Functional Requirements

p95 latency < 500ms for submission endpoint.

99% availability for PoC environment.

PII-safe logging (no sensitive data stored in logs).
