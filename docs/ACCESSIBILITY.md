# Accessibility & Language Support Policy

## Standards
Karing USA targets **WCAG 2.1 AA** compliance.

---

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
