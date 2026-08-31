# Citizen Karen 1.0.0-rc.3

Release date: 2026-08-30

Citizen Karen 1.0.0-rc.3 is the security-refresh build of the full-scale interactive local demo. It includes every capability introduced in 1.0.0-rc.2 while updating two backend dependency pins identified by GitHub Dependabot after that release landed.

## Security refresh

- PyJWT 2.13.0 replaces 2.12.1.
- python-multipart 0.0.31 replaces 0.0.22.
- The updated versions address the open high-, medium-, and low-severity advisories associated with those packages on the default branch.

## Demo boundary

Citizen Karen is an independent civic-tech prototype. It is **not a government service or legal advice**. Agency submissions remain explicitly simulated unless the interface sends the user to an official external destination. This release does not authorize production handling of citizen data or real-agency submission.

## Run locally

```bash
docker compose -f infra/docker-compose.yml up --build
```

See the README, Demo Runbook, Security documentation, and production-readiness issues before presenting or extending the environment.
