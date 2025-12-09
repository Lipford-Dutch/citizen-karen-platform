# Accessibility & Language Support Policy

## Standards
Karing USA targets **WCAG 2.1 AA** compliance.

---

✅ React Stack
  react-aria
  react-i18next
  Lighthouse CI accessibility audit

✅ Legal importance
  Accessibility is not optional for government-adjacent platforms.

## Frontend Requirements

- Full keyboard navigation
- Screen-reader friendly labels
- ARIA roles for dynamic form fields
- 4.5:1 contrast ratio minimum
- Focus traps for modals
- No color-only indicators

---

## Language Support

- English + Spanish required at MVP+
- All user-facing strings must use i18n keys
- No hard-coded English strings in UI

Example:
t("form.phone_number.label")
