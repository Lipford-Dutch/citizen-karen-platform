# KYC‑Lite & Fraud Prevention Policy — Karing USA

Because we act as a gate‑door to many government agencies, we must balance ease of use with protection against abuse. This document outlines lightweight identity verification and abuse prevention strategies.

---

## ✅ When to Require Verification

Require “verified user” status for high‑risk actions such as:  
- Submitting forms to identity- or privacy‑sensitive agencies (e.g. IRS, SSA)  
- Filing identity‑theft / fraud reports  
- Submitting on behalf of others (bulk submissions / enterprise mode)  
- Uploading sensitive documents (PDFs, SSNs, IDs)  

---

## 🔐 Recommended Verification Methods (Tiered)

| Risk Level | Verification Method |
|-----------|---------------------|
| Low / Anonymous complaints | Email + CAPTCHA + rate‑limit (no sensitive PII) |
| Medium | Email + phone verification + CAPTCHA + rate‑limits |
| High (sensitive agencies) | Verified account: email + phone + government ID upload + manual review |

---

## 🔎 Abuse Detection & Monitoring

- Rate‑limit submissions per IP / per email / per account (e.g. 5 submissions/day)  
- Monitor repeated failures / rejections — flag for manual review  
- Use CAPTCHA (or equivalent) to block bots/form‑spam  
- Log all submissions & attempts (with metadata, not PII) for audit  

---

## 📝 Privacy & Fair Use

- For verified users: only store minimal identity metadata (e.g. hashed email, masked phone)  
- Clearly document what data is stored and why (via your privacy / data‑retention docs)  
- If user requests deletion — remove identity metadata + anonymize historic submissions (if allowed by law)  

--- 

## 🔄 Review & Compliance Schedule

- Review this policy quarterly as new agencies/modules are added  
- Update rate‑limit thresholds, verification levels per agency/sensitivity  
- Perform periodic audit of flagged / blocked attempts  

