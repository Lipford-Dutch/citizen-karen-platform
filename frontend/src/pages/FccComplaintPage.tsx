import {
  ArrowRight,
  Building2,
  CircleCheck,
  FileText,
  LockKeyhole,
  Save,
  Send,
  ShieldAlert,
  Trash2,
  UserRound,
} from "lucide-react";
import { type ChangeEvent, type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { type ComplaintInput, submitComplaint } from "../api";


const DRAFT_KEY = "citizen-karen:fcc-draft:v1";
const initialForm: ComplaintInput = {
  agency: "fcc",
  full_name: "",
  email: "",
  phone_number: "",
  complaint_type: "Unwanted calls or texts",
  description: "",
  consent: false,
  consent_version: "2026-08-23",
  website: "",
};

function readDraft(): ComplaintInput {
  try {
    const saved = sessionStorage.getItem(DRAFT_KEY);
    if (!saved) return initialForm;
    const parsed = JSON.parse(saved) as { version: 1; data: ComplaintInput };
    return parsed.version === 1 ? { ...initialForm, ...parsed.data } : initialForm;
  } catch {
    return initialForm;
  }
}

export function FccComplaintPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<ComplaintInput>(readDraft);
  const [reviewing, setReviewing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  const contactComplete = Boolean(form.full_name && form.email);
  const complaintComplete = form.description.trim().length >= 20;
  const activeStep = reviewing ? 3 : contactComplete && complaintComplete ? 2 : contactComplete ? 2 : 1;

  function handleChange(
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) {
    const target = event.target;
    const value = target instanceof HTMLInputElement && target.type === "checkbox"
      ? target.checked
      : target.value;
    setForm((current) => ({ ...current, [target.name]: value }));
    setSaved(false);
    setReviewing(false);
    setError("");
  }

  function saveDraft() {
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify({ version: 1, data: form }));
    setSaved(true);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!reviewing) {
      setReviewing(true);
      return;
    }

    setSubmitting(true);
    try {
      const receipt = await submitComplaint(form);
      sessionStorage.removeItem(DRAFT_KEY);
      navigate(`/track?id=${encodeURIComponent(receipt.tracking_id)}`, {
        state: { receipt },
      });
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "We could not submit this complaint.",
      );
      setReviewing(false);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="form-page page-width" aria-labelledby="fcc-form-heading">
      <div className="form-main">
        <header className="page-intro">
          <h1 id="fcc-form-heading">Tell us what happened.</h1>
          <p>We’ll collect only what the FCC needs for this complaint.</p>
        </header>

        <ol className="form-steps" aria-label="Complaint filing progress">
          {["Contact", "Complaint", "Review"].map((label, index) => {
            const step = index + 1;
            return (
              <li
                className={step < activeStep ? "is-complete" : step === activeStep ? "is-active" : ""}
                key={label}
                aria-current={step === activeStep ? "step" : undefined}
              >
                <span>{step < activeStep ? <CircleCheck aria-hidden="true" /> : step}</span>
                {label}
              </li>
            );
          })}
        </ol>

        <form className="complaint-form" onSubmit={handleSubmit}>
          <div className="field field-full">
            <label htmlFor="full_name">Full name <span aria-hidden="true">*</span></label>
            <input
              id="full_name"
              name="full_name"
              autoComplete="name"
              value={form.full_name}
              onChange={handleChange}
              minLength={2}
              maxLength={120}
              required
            />
          </div>
          <div className="field-grid">
            <div className="field">
              <label htmlFor="email">Email <span aria-hidden="true">*</span></label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="phone_number">Phone number</label>
              <input
                id="phone_number"
                name="phone_number"
                type="tel"
                autoComplete="tel"
                value={form.phone_number}
                onChange={handleChange}
                maxLength={32}
              />
            </div>
          </div>
          <div className="field field-full">
            <label htmlFor="complaint_type">Complaint type <span aria-hidden="true">*</span></label>
            <select
              id="complaint_type"
              name="complaint_type"
              value={form.complaint_type}
              onChange={handleChange}
              required
            >
              <option>Unwanted calls or texts</option>
              <option>Phone service or billing</option>
              <option>Internet service or billing</option>
              <option>TV or radio issue</option>
              <option>Accessibility issue</option>
            </select>
          </div>
          <div className="field field-full">
            <div className="label-row">
              <label htmlFor="description">What happened? <span aria-hidden="true">*</span></label>
              <span>{form.description.length} / 4000</span>
            </div>
            <small id="description-help">Include dates, companies, and what you already tried.</small>
            <textarea
              id="description"
              name="description"
              rows={5}
              value={form.description}
              onChange={handleChange}
              minLength={20}
              maxLength={4000}
              aria-describedby="description-help sensitive-help"
              required
            />
          </div>

          <section className="consent-section" aria-labelledby="consent-heading">
            <h2 id="consent-heading">Before you submit</h2>
            <div className="consent-facts">
              <span><Send aria-hidden="true" /> Send this information to the FCC</span>
              <span><FileText aria-hidden="true" /> Store a tracking record</span>
              <span><Trash2 aria-hidden="true" /> You can request deletion of our copy</span>
            </div>
            <label className="checkbox-row">
              <input
                name="consent"
                type="checkbox"
                checked={form.consent}
                onChange={handleChange}
                required
              />
              <span>
                I authorize Citizen Karen to transmit this complaint to the FCC.
                <span aria-hidden="true"> *</span>
              </span>
            </label>
          </section>

          <div className="honeypot" aria-hidden="true">
            <label htmlFor="website">Website</label>
            <input id="website" name="website" value={form.website} onChange={handleChange} tabIndex={-1} autoComplete="off" />
          </div>

          {reviewing ? (
            <section className="review-panel" aria-live="polite" aria-labelledby="review-heading">
              <CircleCheck aria-hidden="true" />
              <div>
                <h2 id="review-heading">Ready to submit</h2>
                <p>
                  Review your name, contact details, and description above. Your complaint
                  will be sent to the FCC when you continue.
                </p>
              </div>
            </section>
          ) : null}

          {error ? <p className="form-error" role="alert">{error}</p> : null}

          <div className="form-actions">
            <button className="button button-secondary" type="button" onClick={saveDraft}>
              <Save aria-hidden="true" /> Save for this tab
            </button>
            <button className="button button-primary" type="submit" disabled={submitting}>
              {submitting ? "Submitting…" : reviewing ? "Submit to FCC" : "Review complaint"}
              <ArrowRight aria-hidden="true" />
            </button>
          </div>
          <p className="save-status" role="status">
            {saved ? "Draft saved in this browser tab. It clears when the tab closes." : "Nothing is saved until you choose to save or submit."}
          </p>
        </form>
      </div>

      <aside className="privacy-glance" aria-labelledby="privacy-glance-heading">
        <div className="map-dash" aria-hidden="true" />
        <h2 id="privacy-glance-heading"><LockKeyhole aria-hidden="true" /> Your privacy at a glance</h2>
        <ul>
          <li><UserRound aria-hidden="true" /><span><strong>No account required</strong>You can file without creating an account.</span></li>
          <li><ShieldAlert aria-hidden="true" /><span><strong>We do not sell complaint data</strong>Your information is used to process and track this complaint.</span></li>
          <li><Building2 aria-hidden="true" /><span><strong>The FCC keeps its own copy</strong>The FCC is an independent agency and controls its records.</span></li>
        </ul>
        <Link to="/privacy">Read the privacy notice <ArrowRight aria-hidden="true" /></Link>
        <p id="sensitive-help" className="sensitive-note">
          <ShieldAlert aria-hidden="true" />
          Do not include Social Security numbers, passwords, or payment card details.
        </p>
      </aside>
    </section>
  );
}
