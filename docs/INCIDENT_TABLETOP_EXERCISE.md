# Incident Response — Tabletop Exercise Template

Purpose: To rehearse how Karing USA team responds to a critical incident (data breach, PII leak, upstream API failure, mass failure, etc.)

---

## 🚨 Sample Scenario (template)

**Scenario:** A recently deployed update to one agency module causes submissions to fail silently (status “pending forever”). Simultaneously, retry‑logic triggers 1000+ retries in 10 minutes → queue backlog, user complaints, possible DDoS detection.

### Steps

1. Detection: Monitoring alert fires (queue backlog > threshold OR high retry count)  
2. Triage: On‑call engineer reviews logs, identifies failing module + error trace  
3. Containment: Pause job queue; disable that module; revert deploy if needed  
4. Communication: Post status update on admin dashboard / public status page; send email to affected users  
5. Remediation: Fix module logic, run tests, clean backlog, resume queue with patches  
6. Post‑mortem & Documentation: Log incident timeline, root cause, mitigation, lessons learned  

---

## 🎯 Roles & Responsibilities

- **On‑call engineer / Backend lead** — triage, debugging, patch  
- **DevOps / Infra lead** — manage queue, rollback, deployment, database state  
- **Security contact** — assess potential data breach / PII exposure  
- **Communications lead** — status updates, user notification, public transparency  
- **Documentation owner** — fill incident log, post‑mortem, update SOP  

---

## 📄 Post‑Incident Report Template

- Incident ID & Timestamp  
- Description & Impact (how many submissions affected, user-facing error, data integrity risk)  
- Root Cause (code bug, upstream change, data issue, config problem)  
- Action Taken (rollback, patch, module disable)  
- Remediation Steps & Timeline  
- Lessons Learned & Preventive Measures  
- Adjustments to Monitoring / Alerting / Module Health Checks  

---

## 🔁 Drill Frequency & Audit

- Perform tabletop exercise **every 6 months** (or after major release)  
- Review & update incident plan based on real incidents or drills  
- Ensure contact lists / alerting configuration is up‑to-date  
