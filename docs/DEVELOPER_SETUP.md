# Developer setup

## Prerequisites

- Python 3.14
- Node.js 24 and npm
- Docker Desktop with Compose v2 for the packaged stack

## Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Local backend development defaults to SQLite at `backend/data/citizen-karen.db` so contributors can run without infrastructure. Set `DATABASE_URL` to use another SQLAlchemy database URL. API documentation is at <http://localhost:8000/api/docs>.

## Frontend

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Vite proxies API calls to <http://localhost:8000>.

## Complete Docker stack

```bash
docker compose -f infra/docker-compose.yml up --build
```

The packaged app is at <http://localhost:8080>. Compose uses Alembic-managed Postgres as its source of truth, Redis and Celery for background work, and the network mock FCC connector. Named volumes preserve Postgres, Redis, Prometheus, and Grafana state.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ENV` | `local` | Runtime safety profile: `local`, `test`, `staging`, or `production` |
| `DATABASE_URL` | local SQLite URL | SQLAlchemy database URL; Compose supplies Postgres |
| `CORS_ORIGINS` | local Vite origins | Comma-separated browser origins |
| `FCC_CONNECTOR_MODE` | `simulate` | `simulate` or `network` |
| `FCC_API_URL` | local mock endpoint | Endpoint used in network mode |
| `FCC_APPROVED_ENDPOINTS` | empty | Exact comma-separated HTTPS FCC endpoints allowed in staging/production; a listed non-default port is explicitly allowed |
| `REDIS_URL` | local Redis URL | Celery broker and result backend |
| `INSECURE_INTERNAL_HOSTS` | empty | Exact hosts allowed to use cleartext Redis, OTLP, FCC, or PostgreSQL transport in staging/production; no host is trusted implicitly |
| `DEMO_MODE` | `true` in Compose | Enables synthetic demo identities and seeded walkthroughs |

Never put production complaint data or credentials in `.env` files checked into Git.

Generate shared-environment JWT secrets with `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Validation requires URL-safe base64 that decodes to at least 32 bytes, at least 16 distinct encoded characters, at least 4 bits of Shannon entropy per encoded character, no periodic or repeated-substring pattern, and no common demo or placeholder markers. These checks are format and quality guards, not proof that a secret was generated randomly; use the documented generator rather than constructing a token manually. Production CORS values must be canonical HTTPS origins such as `https://app.example.com` with no wildcard, path, credentials, query, or fragment. `FCC_API_URL` must exactly match an entry in `FCC_APPROVED_ENDPOINTS`; an explicit matching entry is also how a non-default HTTPS port is authorized. IP literals in loopback, private, and link-local ranges are always rejected.

In staging and production, external Redis uses `rediss://`, external OTLP uses `https://`, and external PostgreSQL uses `sslmode=require` or `sslmode=verify-full`. Cleartext transport is permitted only when the exact destination host appears in `INSECURE_INTERNAL_HOSTS`; short Docker service names are not trusted automatically. The Compose demo explicitly lists its controlled internal service names. SQLite is local/test-only.

## Quality commands

```bash
cd backend
python -m ruff check .
python -m ruff format --check .
python -m mypy app --ignore-missing-imports
python -m pytest --cov=app --cov-fail-under=90

cd ../frontend
npm run lint
npm test
npm run build
npm audit --audit-level=high
```

From the repository root:

```bash
python -m pip install -r requirements-docs.txt
python -m mkdocs build --strict
docker compose -f infra/docker-compose.yml config --quiet
```

## Agency integrations

FCC can route to the repository-owned network mock. Every other registered plugin is an explicit local simulation. Add a real connector only after completing the legal-risk, consent, data-minimization, failure-mode, accessibility, and test review in the [agency plugin guide](AGENCY_PLUGIN_GUIDE.md).
