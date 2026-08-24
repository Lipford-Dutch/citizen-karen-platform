# Citizen Karen

Citizen Karen is a consent-first civic complaint navigator. The Day-1 release helps people find 28 official federal complaint destinations, file an FCC complaint through a working intake flow, keep a tracking receipt, and delete the complaint content retained by the local service.

> [!IMPORTANT]
> This repository is an engineering release candidate, not a government service or legal advice. The default connector simulates FCC acceptance; every other directory entry sends the user to the agency's official website. Do not deploy the prototype to the public internet without the production controls listed in [Security](SECURITY.md).

## What works

- Searchable, deduplicated directory built from the local complaint-source workbook and research notes
- Responsive React 19 interface with semantic navigation, keyboard support, reduced-motion handling, and automated axe checks
- Consent-gated FCC form with review step, draft recovery, anti-bot honeypot, and sensitive-number rejection
- FastAPI submission, durable SQLite receipt, PII-safe structured logs, Prometheus metrics, and request security headers
- Tracking timeline with agency reference, copy action, and local-content deletion
- Simulated connector for zero-credential local use plus a network mock for the Docker stack
- Reproducible frontend, backend, mock-agency, and reverse-proxy containers

## Run the complete stack

Requirements: Docker Desktop with Compose v2.

```bash
docker compose -f infra/docker-compose.yml up --build
```

Open <http://localhost:8080>. The API is also exposed at <http://localhost:8000>, with interactive docs at <http://localhost:8000/api/docs>. Stop the stack with:

```bash
docker compose -f infra/docker-compose.yml down
```

The named `complaint-data` volume preserves local receipts. Use `docker compose -f infra/docker-compose.yml down --volumes` only when you intentionally want to remove them.

## Develop locally

Backend (Python 3.14):

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Frontend (Node.js 24):

```bash
cd frontend
npm ci
npm run dev
```

Vite proxies `/api` to the backend at port 8000. The default backend connector uses a safe simulation and needs no account or API key.

## Verify

```bash
cd backend
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=app --cov-fail-under=90

cd ../frontend
npm run lint
npm test
npm run build
npm audit --audit-level=high

cd ..
docker compose -f infra/docker-compose.yml config --quiet
python -m mkdocs build --strict
```

## Architecture

```text
Browser → nginx SPA/reverse proxy → FastAPI → SQLite receipt store
                                      └────→ FCC connector
                                              ├─ simulation (local default)
                                              └─ mock FCC service (Compose)
```

The curated directory never pretends unsupported agencies have automated integrations. FCC is the only direct Day-1 flow; all other entries clearly open official external destinations.

## Repository map

- `frontend/` — TypeScript, React, Vite, UI tests, and production nginx image
- `backend/` — FastAPI app, SQLite store, FCC plugin, metrics, and pytest suite
- `api/openapi.yaml` — checked-in OpenAPI 3.1 contract
- `infra/` — Compose stack and service images
- `docs/` — product, accessibility, security, consent, architecture, and handoff material
- `docs/design/` — accepted visual concepts and implementation notes

See [Developer setup](docs/DEVELOPER_SETUP.md), [release handoff](docs/HANDOFF.md), [security policy](SECURITY.md), and [contributing guide](CONTRIBUTING.md).

## License

[MIT](LICENSE)
