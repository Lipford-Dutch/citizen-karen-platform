import { Bug, FileKey2, ScrollText, ShieldCheck } from "lucide-react";


export function SecurityPage() {
  return (
    <article className="policy-page page-width">
      <header className="policy-hero">
        <h1>Security without mystery.</h1>
        <p>
          The Day-1 package minimizes stored fields, excludes complaint content from logs,
          validates consent, and makes local deletion testable.
        </p>
      </header>
      <section className="policy-summary">
        <div><FileKey2 aria-hidden="true" /><strong>No secrets in the client</strong><span>Runtime endpoints are configured through environment variables and same-origin proxying.</span></div>
        <div><ScrollText aria-hidden="true" /><strong>PII-safe logs</strong><span>Logs include request and tracking metadata, never form names, email, phone, or complaint text.</span></div>
        <div><ShieldCheck aria-hidden="true" /><strong>Defensive defaults</strong><span>Security headers, strict validation, honeypot filtering, and explicit CORS origins are enabled.</span></div>
      </section>
      <div className="policy-body">
        <section>
          <h2><Bug aria-hidden="true" /> Report a vulnerability</h2>
          <p>
            Follow the responsible-disclosure process in the repository’s SECURITY.md.
            Do not open a public issue containing exploit details, credentials, or personal data.
          </p>
        </section>
        <section>
          <h2>Production boundary</h2>
          <p>
            The built-in connector simulation and mock FCC service are development tools.
            Real public submission requires agency authorization, TLS termination, managed
            secrets, encrypted storage, abuse controls, backups, and an approved legal review.
          </p>
        </section>
      </div>
    </article>
  );
}
