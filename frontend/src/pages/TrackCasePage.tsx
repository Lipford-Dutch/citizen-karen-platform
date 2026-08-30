import {
  ArrowRight,
  Building2,
  CalendarDays,
  Check,
  CircleHelp,
  Clock3,
  Copy,
  ExternalLink,
  Search,
  Trash2,
  TriangleAlert,
  Upload,
  X,
} from "lucide-react";
import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";

import {
  type ComplaintReceipt,
  type ComplaintStatus,
  deleteComplaintCopy,
  getComplaintStatus,
  uploadEvidence,
} from "../api";


function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export function TrackCasePage() {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const receipt = (location.state as { receipt?: ComplaintReceipt } | null)?.receipt;
  const initialId = searchParams.get("id") ?? receipt?.tracking_id ?? "";
  const [autoLookupId] = useState(initialId);
  const [trackingId, setTrackingId] = useState(initialId);
  const [caseStatus, setCaseStatus] = useState<ComplaintStatus | null>(null);
  const [loading, setLoading] = useState(Boolean(initialId));
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [evidenceStatus, setEvidenceStatus] = useState("");
  const deleteButtonRef = useRef<HTMLButtonElement>(null);
  const deleteDialogRef = useRef<HTMLElement>(null);

  const closeDeleteDialog = useCallback(() => {
    setShowDelete(false);
    window.setTimeout(() => deleteButtonRef.current?.focus(), 0);
  }, []);

  useEffect(() => {
    if (!autoLookupId) return;
    let active = true;
    getComplaintStatus(autoLookupId)
      .then((status) => {
        if (active) setCaseStatus(status);
      })
      .catch((lookupError: unknown) => {
        if (active) {
          setError(lookupError instanceof Error ? lookupError.message : "Complaint not found.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [autoLookupId]);

  useEffect(() => {
    if (!showDelete) return;
    const dialog = deleteDialogRef.current;
    const focusable = dialog?.querySelectorAll<HTMLElement>(
      "button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex='-1'])",
    );
    focusable?.[0]?.focus();

    function handleDialogKeys(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        closeDeleteDialog();
        return;
      }
      if (event.key !== "Tab" || !focusable?.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleDialogKeys);
    return () => document.removeEventListener("keydown", handleDialogKeys);
  }, [closeDeleteDialog, showDelete]);

  async function lookup(event: FormEvent) {
    event.preventDefault();
    const normalized = trackingId.trim().toUpperCase();
    setError("");
    setCaseStatus(null);
    setLoading(true);
    try {
      const result = await getComplaintStatus(normalized);
      setCaseStatus(result);
      setSearchParams({ id: normalized }, { replace: true });
    } catch (lookupError) {
      setError(lookupError instanceof Error ? lookupError.message : "Complaint not found.");
    } finally {
      setLoading(false);
    }
  }

  async function copyTrackingId() {
    if (!caseStatus) return;
    await navigator.clipboard.writeText(caseStatus.tracking_id);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2400);
  }

  async function confirmDelete() {
    if (!caseStatus) return;
    setDeleting(true);
    setError("");
    try {
      await deleteComplaintCopy(caseStatus.tracking_id);
      setCaseStatus((current) => current ? { ...current, state: "deleted" } : null);
      setShowDelete(false);
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Deletion failed.");
    } finally {
      setDeleting(false);
    }
  }

  async function attachEvidence(file: File | undefined) {
    if (!caseStatus || !file) return;
    setEvidenceStatus("Scanning locally…");
    try {
      const result = await uploadEvidence(caseStatus.tracking_id, file);
      setEvidenceStatus(`Evidence ${result.scan_status}. Scheduled for deletion in ${result.retention_days} days.`);
    } catch (uploadError) {
      setEvidenceStatus(uploadError instanceof Error ? uploadError.message : "Evidence upload failed.");
    }
  }

  return (
    <section className="track-page page-width" aria-labelledby="track-heading">
      <header className="page-intro">
        <h1 id="track-heading">See where your complaint stands.</h1>
        <p>Enter the tracking ID you received after filing.</p>
      </header>

      <form className="tracking-search" onSubmit={lookup}>
        <label htmlFor="tracking-id">Tracking ID</label>
        <div>
          <input
            id="tracking-id"
            value={trackingId}
            onChange={(event) => setTrackingId(event.target.value)}
            placeholder="CK-2026-8F3A9C"
            autoComplete="off"
            required
          />
          <button className="button button-primary" type="submit" disabled={loading}>
            <Search aria-hidden="true" />
            {loading ? "Checking…" : "Check status"}
          </button>
        </div>
      </form>

      {receipt ? (
        <p className="success-banner" role="status">
          <Check aria-hidden="true" /> Complaint received. Save this tracking ID.
        </p>
      ) : null}
      {error ? <p className="form-error" role="alert">{error}</p> : null}

      <div className="track-layout">
        {caseStatus ? (
          <article className="case-card" aria-labelledby="case-title">
            <header>
              <div>
                <h2 id="case-title">{caseStatus.agency.toUpperCase()} complaint</h2>
                <p className={`case-state state-${caseStatus.state}`}>
                  <Check aria-hidden="true" />
                  {caseStatus.state === "deleted" ? "Local copy deleted" : caseStatus.state.replaceAll("_", " ")}
                </p>
              </div>
              <div className="tracking-id-block">
                <span>Tracking ID</span>
                <strong>{caseStatus.tracking_id}</strong>
              </div>
            </header>

            <ol className="case-timeline" aria-label="Complaint status timeline">
              <li className="is-complete"><span><Check aria-hidden="true" /></span><strong>Received</strong><small>{formatDate(caseStatus.submitted_at)}</small></li>
              <li className={caseStatus.state !== "deleted" ? "is-complete" : ""}><span><Check aria-hidden="true" /></span><strong>Queued to connector</strong><small>{formatDate(caseStatus.last_updated)}</small></li>
              <li><span>3</span><strong>Agency response</strong><small>Waiting for an update</small></li>
            </ol>

            <dl className="case-metadata">
              <div><CalendarDays aria-hidden="true" /><dt>Submitted</dt><dd>{formatDate(caseStatus.submitted_at)}</dd></div>
              <div><Clock3 aria-hidden="true" /><dt>Last updated</dt><dd>{formatDate(caseStatus.last_updated)}</dd></div>
              <div><Building2 aria-hidden="true" /><dt>Agency reference</dt><dd>{caseStatus.agency_reference ?? "Pending"}</dd></div>
            </dl>

            <div className="case-actions">
              <button type="button" onClick={copyTrackingId}><Copy aria-hidden="true" /> Copy tracking ID</button>
              <Link to="/directory"><ExternalLink aria-hidden="true" /> Official directory</Link>
              <button ref={deleteButtonRef} className="danger-link" type="button" onClick={() => setShowDelete(true)} disabled={caseStatus.state === "deleted"}><Trash2 aria-hidden="true" /> Request deletion</button>
            </div>
            {caseStatus.state !== "deleted" ? <label className="evidence-upload"><Upload aria-hidden="true" /><span><strong>Attach evidence</strong><small>PDF, PNG, JPEG, or text · 5 MB · local malware-scan stub · 30-day retention</small></span><input type="file" accept=".pdf,.png,.jpg,.jpeg,.txt" onChange={(event) => void attachEvidence(event.target.files?.[0])} /></label> : null}
            {evidenceStatus ? <p className="save-status" role="status">{evidenceStatus}</p> : null}
            {caseStatus.events?.length ? <details className="audit-events"><summary>View immutable audit trail ({caseStatus.events.length} events)</summary><ol>{caseStatus.events.map((event, index) => <li key={`${event.type}-${index}`}><Check aria-hidden="true" /><strong>{event.type.replaceAll("_", " ")}</strong><time>{formatDate(event.occurred_at)}</time></li>)}</ol></details> : null}
            {copied ? <p className="copy-toast" role="status"><Check aria-hidden="true" /> Tracking ID copied</p> : null}
          </article>
        ) : (
          <div className="track-empty">
            <Search aria-hidden="true" />
            <h2>Ready when you are</h2>
            <p>Your tracking ID begins with CK and appears on the receipt after filing.</p>
          </div>
        )}

        <aside className="next-steps" aria-labelledby="next-steps-heading">
          <div className="map-dash" aria-hidden="true" />
          <h2 id="next-steps-heading"><CircleHelp aria-hidden="true" /> What happens next?</h2>
          <p>Demo connector state is shown here after successful queueing.</p>
          <p>Agency interactions in this environment are simulated. No status shown here is a real agency determination.</p>
          <Link to="/privacy">How status tracking works <ArrowRight aria-hidden="true" /></Link>
        </aside>
      </div>

      {showDelete ? (
        <div className="modal-backdrop" role="presentation" onMouseDown={closeDeleteDialog}>
          <section ref={deleteDialogRef} className="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="delete-heading" onMouseDown={(event) => event.stopPropagation()}>
            <button className="dialog-close" type="button" aria-label="Close deletion confirmation" onClick={closeDeleteDialog}><X aria-hidden="true" /></button>
            <TriangleAlert aria-hidden="true" />
            <h2 id="delete-heading">Request deletion of this case?</h2>
            <p>This deletes complaint content and evidence stored by Citizen Karen. It cannot delete a real agency’s separate copy when one exists.</p>
            <div>
              <button className="button button-secondary" type="button" onClick={closeDeleteDialog}>Cancel</button>
              <button className="button button-danger" type="button" onClick={confirmDelete} disabled={deleting}>{deleting ? "Deleting…" : "Delete local copy"}</button>
            </div>
          </section>
        </div>
      ) : null}
    </section>
  );
}
