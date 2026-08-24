import { ArrowRight, Building2, Clock3, Database, Eye, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";


export function PrivacyPage() {
  return (
    <article className="policy-page page-width">
      <header className="policy-hero">
        <h1>Your complaint. Your choice.</h1>
        <p>
          This notice explains what Citizen Karen stores when you file directly,
          what goes to an agency, and how to delete our copy.
        </p>
        <small>Notice version 2026-08-23</small>
      </header>

      <section className="policy-summary" aria-label="Privacy summary">
        <div><Database aria-hidden="true" /><strong>What we collect</strong><span>Contact details, complaint type, complaint text, consent version, and tracking metadata.</span></div>
        <div><Building2 aria-hidden="true" /><strong>Who receives it</strong><span>For direct FCC filing, the FCC receives the complaint information you review and authorize.</span></div>
        <div><Trash2 aria-hidden="true" /><strong>What you control</strong><span>You can delete Citizen Karen’s stored complaint copy from the tracking page.</span></div>
      </section>

      <div className="policy-body">
        <section>
          <h2><Eye aria-hidden="true" /> How the directory works</h2>
          <p>
            Most directory results open an official agency website. Citizen Karen
            does not receive or store what you submit on those external sites.
          </p>
        </section>
        <section>
          <h2><Database aria-hidden="true" /> Direct FCC filing</h2>
          <p>
            We store the fields shown in the FCC form so we can transmit the complaint,
            create a tracking record, and display its status. We also record the version
            of the consent notice you accepted and operational events such as receipt,
            submission, and deletion.
          </p>
          <p>
            Do not include Social Security numbers, passwords, payment card details, or
            information that is not needed for your complaint. The API rejects common
            Social Security and payment-card number patterns.
          </p>
        </section>
        <section>
          <h2><Clock3 aria-hidden="true" /> Retention and deletion</h2>
          <p>
            The Day-1 implementation keeps a local tracking copy until you delete it.
            A production retention schedule must be approved through legal and governance
            review before handling real public submissions.
          </p>
          <p>
            Deleting from Citizen Karen redacts the locally stored complaint payload and
            leaves a minimal event record showing that deletion occurred. It does not
            delete records held independently by the FCC or another official website.
          </p>
        </section>
        <section>
          <h2><Building2 aria-hidden="true" /> Important boundary</h2>
          <p>
            Citizen Karen is an independent civic-technology project, not a government
            agency. Agencies control their own review processes, response times, and data.
          </p>
        </section>
      </div>

      <div className="policy-actions">
        <Link className="button button-primary" to="/track">Manage a tracking record <ArrowRight aria-hidden="true" /></Link>
        <Link className="button button-secondary" to="/file">Review the FCC form</Link>
      </div>
    </article>
  );
}
