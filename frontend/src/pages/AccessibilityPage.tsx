import { Keyboard, Languages, MousePointer2, Volume2 } from "lucide-react";


export function AccessibilityPage() {
  return (
    <article className="policy-page page-width">
      <header className="policy-hero">
        <h1>Accessibility is part of the product.</h1>
        <p>
          Citizen Karen is designed for keyboard, screen-reader, zoom, reduced-motion,
          and high-contrast use. We target WCAG 2.2 AA for the public interface.
        </p>
      </header>
      <section className="policy-summary">
        <div><Keyboard aria-hidden="true" /><strong>Keyboard first</strong><span>Visible focus, logical reading order, skip navigation, and no mouse-only actions.</span></div>
        <div><Volume2 aria-hidden="true" /><strong>Clear announcements</strong><span>Errors, loading, saved drafts, copied IDs, and results use live regions.</span></div>
        <div><MousePointer2 aria-hidden="true" /><strong>Comfortable targets</strong><span>Controls use generous sizing, contrast, labels, and predictable states.</span></div>
      </section>
      <div className="policy-body">
        <section>
          <h2><Languages aria-hidden="true" /> Known next step</h2>
          <p>
            Spanish localization is part of the repository readiness plan but is not yet
            implemented. The current release keeps plain-language English copy centralized
            and structured for a future translation pass.
          </p>
        </section>
        <section>
          <h2>Report a barrier</h2>
          <p>
            Open an accessibility issue in the project’s GitHub repository. Include the
            page, browser, assistive technology, and what you expected to happen. Do not
            include complaint content or personal information.
          </p>
        </section>
      </div>
    </article>
  );
}
