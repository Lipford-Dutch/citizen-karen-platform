# Data Governance & Retention Policy — Karing USA

## Purpose
This document defines how citizen data is collected, stored, retained, accessed, and deleted across all agencies. It establishes Karing USA as a compliant, auditable system-of-record (SOT).

---

## Data Classification

| Classification | Examples | Storage Rules |
|----------------|----------|---------------|
| Public Metadata | Agency name, submission timestamps | Stored unencrypted |
| Sensitive PII | Name, phone, email, complaint body | Encrypted at rest |
| High-Risk PII | SSN, EIN, DOB (rare) | Encrypted + access logged |
| Derived Data | Metrics, aggregates | Must be de-identified |

---

## Retention Policy (Default)

| Agency | Retention |
|------|-----------|
| FCC | 3 years |
| IRS | 7 years |
| SSA | 5–10 years (configurable) |
| State Agencies | Configurable per jurisdiction |
| Audit Logs | 10 years (immutable) |
| Metrics (non-PII) | Indefinite |

> Retention is **per-agency configurable** and enforced by scheduled purge jobs.

---

## Deletion & Right to Erasure

- Users may request deletion unless blocked by legal hold
- Requests processed within 30 days
- Deletion includes:
  - Payload redaction
  - Tombstone record for audit
- External agencies **are not guaranteed deletion** (disclosed in consent)

---

## Access Controls

- RBAC required for viewing PII
- All accesses logged
- Read/write operations tracked by actor + timestamp
