SECURITY HARDENING
(SECURITY_ARCHITECTURE.md + Code Hooks)
Threat Model (Minimum Viable)
Threat	Mitigation
API abuse / spam	Rate limits + CAPTCHA
Credential leakage	Secrets scanning + rotation
PII in logs	Log sanitizer middleware
Dependency compromise	Lockfiles + CVE scanning
Insider abuse	Access logs + RBAC
