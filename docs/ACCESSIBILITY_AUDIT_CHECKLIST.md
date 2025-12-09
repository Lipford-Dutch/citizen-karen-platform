# Accessibility Audit Checklist — Karing USA

Ensure your frontend (citizen + admin UI) meets WCAG 2.1 AA standards and is inclusive.

## ✅ Audit Items

### Semantics & Structure
- Use semantic HTML (`<header>`, `<main>`, `<nav>`, `<footer>`, `<form>`, `<label>`, etc.)  
- All form inputs have associated `<label>` tags  
- Proper `alt` text for images/icons; decorative images marked via `aria-hidden="true"` or empty alt  

### Keyboard Navigation
- All interactive elements accessible via Tab / Enter / Space  
- Focus styles visible and clear (not just color, also outline or underline)  
- No “focus traps” / ensure modals & dialogs manage focus properly  

### Contrast & Visual Design
- All text meets contrast ratio ≥ 4.5:1 (normal) or ≥ 3:1 (large)  
- Color is never the only means of conveying information (use icons, labels, underlines)  
- UI scalable / responsive — layout works at zoom up to 200%  

### ARIA / Assistive Support
- Use ARIA roles where appropriate (e.g. `role="alert"`, `aria-live`, `aria-label`)  
- Dynamic content updates (status changes, error messages) announced properly via ARIA live regions  
- Skip navigation or “skip to content” link at top for screen‑reader users  

### Form & Error Handling
- Clear, descriptive error messages  
- Associate error messages with inputs via `aria-describedby` / `aria-invalid`  
- Provide accessible validation (not just color)  

### Language & Internationalization
- UI supports at least English + Spanish  
- Strings not hard‑coded; use i18n framework  
- Date/time formats, error messages, placeholders localized  

### Testing & Audit Tools
- Use automated tools: *axe*, *eslint-plugin-jsx-a11y*, *react-axe*  
- Manual keyboard-only navigation testing  
- Screen‑reader testing (NVDA, VoiceOver)  
- Zoom / high‑contrast mode & responsive/mobile testing  

