import { ArrowLeft, ArrowRight, Check, ExternalLink, ShieldAlert } from "lucide-react";
import { type FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { type ComplaintInput, type PluginManifest, getPlugins, submitComplaint } from "../api";

export function DynamicComplaintPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [plugins, setPlugins] = useState<PluginManifest[]>([]);
  const [agency, setAgency] = useState(searchParams.get("agency") ?? "fcc");
  const [step, setStep] = useState(0);
  const [values, setValues] = useState<Record<string, string | boolean>>({});
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { getPlugins().then((result) => setPlugins(result.plugins)).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Plugin catalog unavailable")); }, []);
  const plugin = useMemo(() => plugins.find((item) => item.key === agency), [agency, plugins]);
  const fields = plugin ? Object.entries(plugin.form_schema.properties) : [];

  function advance(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (step < 2) setStep((current) => current + 1);
  }

  async function submit() {
    if (!plugin || !consent) return;
    setSubmitting(true);
    setError("");
    const input: ComplaintInput = {
      agency: plugin.key,
      full_name: String(values.full_name ?? ""),
      email: String(values.email ?? ""),
      phone_number: String(values.phone_number ?? ""),
      complaint_type: String(values.complaint_type ?? "General issue"),
      description: String(values.description ?? ""),
      consent,
      consent_version: "2026-08-23",
      website: "",
      dynamic_fields: values,
    };
    try {
      const receipt = await submitComplaint(input);
      navigate(`/track?id=${encodeURIComponent(receipt.tracking_id)}`, { state: { receipt } });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Submission could not be queued");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="dynamic-form-page page-width" aria-labelledby="dynamic-form-heading">
      <header className="dynamic-form-header">
        <div><h1 id="dynamic-form-heading">File a guided complaint.</h1><p>Every integration on this page is a local simulation. You can always use the official agency site instead.</p></div>
        <ol aria-label="Filing progress"><li className={step >= 0 ? "active" : ""}><span>1</span>Agency</li><li className={step >= 1 ? "active" : ""}><span>2</span>Details</li><li className={step >= 2 ? "active" : ""}><span>3</span>Review</li></ol>
      </header>
      {step === 0 ? <section className="agency-picker" aria-labelledby="choose-agency"><h2 id="choose-agency">Choose a demo agency plugin</h2><p>Risk and verification requirements come from the plugin manifest.</p><div>{plugins.map((item) => <button type="button" key={item.key} className={agency === item.key ? "selected" : ""} onClick={() => setAgency(item.key)} aria-pressed={agency === item.key}><strong>{item.short_name}</strong><span>{item.name}</span><small>{item.risk_level} risk · KYC {item.kyc_level} · {item.simulated ? "simulated" : "connected"}</small></button>)}</div>{plugin ? <aside className="plugin-boundary"><ShieldAlert aria-hidden="true" /><div><strong>{plugin.automation}</strong><span>{plugin.restrictions.join(" · ")}</span><a href={plugin.official_url} target="_blank" rel="noreferrer">Open official website <ExternalLink aria-hidden="true" /></a></div></aside> : null}<button className="button button-primary" type="button" onClick={() => setStep(1)} disabled={!plugin}>Continue <ArrowRight aria-hidden="true" /></button></section> : null}
      {step === 1 && plugin ? <form className="schema-form" onSubmit={advance}><h2>{plugin.form_schema.title}</h2><p>Fields and validation are rendered from the {plugin.short_name} plugin schema.</p>{fields.map(([key, field]) => <label key={key} className={field.format === "textarea" ? "field-wide" : ""}><span>{field.title}{plugin.form_schema.required.includes(key) ? " *" : ""}</span>{field.type === "boolean" ? <input type="checkbox" checked={Boolean(values[key])} onChange={(event) => setValues({ ...values, [key]: event.target.checked })} /> : field.enum ? <select required={plugin.form_schema.required.includes(key)} value={String(values[key] ?? "")} onChange={(event) => setValues({ ...values, [key]: event.target.value })}><option value="">Select one</option>{field.enum.map((choice) => <option key={choice}>{choice}</option>)}</select> : field.format === "textarea" ? <textarea required={plugin.form_schema.required.includes(key)} minLength={field.minLength} maxLength={field.maxLength} value={String(values[key] ?? "")} onChange={(event) => setValues({ ...values, [key]: event.target.value })} /> : <input type={field.format === "email" ? "email" : "text"} required={plugin.form_schema.required.includes(key)} minLength={field.minLength} value={String(values[key] ?? "")} onChange={(event) => setValues({ ...values, [key]: event.target.value })} />}</label>)}<div className="form-actions"><button className="button button-secondary" type="button" onClick={() => setStep(0)}><ArrowLeft aria-hidden="true" />Back</button><button className="button button-primary" type="submit">Review <ArrowRight aria-hidden="true" /></button></div></form> : null}
      {step === 2 && plugin ? <section className="review-submission"><h2>Review and explicitly authorize</h2><p>Citizen Karen will queue this complaint to the <strong>simulated {plugin.short_name} connector</strong>. No real agency receives this demo submission.</p><dl>{fields.filter(([key]) => values[key] !== undefined).map(([key, field]) => <div key={key}><dt>{field.title}</dt><dd>{typeof values[key] === "boolean" ? (values[key] ? "Yes" : "No") : String(values[key])}</dd></div>)}</dl><label className="consent-check"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} /><span><strong>I authorize Citizen Karen to process and transmit this complaint to the selected simulated connector.</strong>I understand this demo is not a government service or legal advice and that my consent record will be stored.</span></label>{error ? <p className="form-error" role="alert">{error}</p> : null}<div className="form-actions"><button className="button button-secondary" type="button" onClick={() => setStep(1)}><ArrowLeft aria-hidden="true" />Edit details</button><button className="button button-primary" type="button" disabled={!consent || submitting} onClick={submit}><Check aria-hidden="true" />{submitting ? "Queuing…" : "Submit simulated complaint"}</button></div></section> : null}
      {error && step !== 2 ? <p className="form-error" role="alert">{error}</p> : null}
    </section>
  );
}
