import {
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  Clock3,
  FolderOpen,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { type CaseSummary, demoLogin, getCases, retryComplaint } from "../api";

type Filter = "all" | "active" | "attention" | "resolved";

const labels: Record<string, string> = {
  received: "Queued",
  submitted: "Submitted",
  acknowledged: "Acknowledged",
  under_review: "Under review",
  resolved: "Resolved",
  rejected: "Rejected",
  retrying: "Retrying",
  needs_attention: "Needs attention",
  escalated: "Escalated",
  deleted: "Local copy deleted",
};

const agencyNames: Record<string, string> = {
  fcc: "Federal Communications Commission",
  cfpb: "Consumer Financial Protection Bureau",
  epa: "Environmental Protection Agency",
  irs: "Internal Revenue Service",
  "state-dmv": "Example State DMV",
  ftc: "Federal Trade Commission",
  "failure-lab": "Reliability Test Agency",
  benefits: "Public Benefits Navigator",
};

function date(value: string | null) {
  if (!value) return "No action needed";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export function CommandCenterPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retrying, setRetrying] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    demoLogin("citizen")
      .then(() => getCases())
      .then((result) => { if (active) setCases(result.cases); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Command Center unavailable"); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const activeCases = cases.filter((item) => !["resolved", "deleted"].includes(item.status));
  const attention = cases.filter((item) => ["needs_attention", "retrying", "escalated"].includes(item.status));
  const resolved = cases.filter((item) => item.status === "resolved");
  const filtered = useMemo(() => cases.filter((item) => {
    if (filter === "active") return !["resolved", "deleted"].includes(item.status);
    if (filter === "attention") return ["needs_attention", "retrying", "escalated"].includes(item.status);
    if (filter === "resolved") return item.status === "resolved";
    return true;
  }), [cases, filter]);

  async function retry(trackingId: string) {
    setRetrying(trackingId);
    try {
      await retryComplaint(trackingId);
      setCases((current) => current.map((item) => item.tracking_id === trackingId ? { ...item, status: "retrying", retry_count: item.retry_count + 1 } : item));
    } finally {
      setRetrying(null);
    }
  }

  return (
    <div className="command-layout page-width">
      <section className="command-main" aria-labelledby="command-heading">
        <header className="command-intro">
          <h1 id="command-heading">Your cases, clearly organized.</h1>
          <p>Track progress, review next steps, and keep control of your information.</p>
        </header>

        <dl className="case-stats">
          <div><FolderOpen aria-hidden="true" /><dt>Active cases</dt><dd>{activeCases.length}</dd></div>
          <div className="stat-attention"><AlertTriangle aria-hidden="true" /><dt>Needs attention</dt><dd>{attention.length}</dd></div>
          <div><CheckCircle2 aria-hidden="true" /><dt>Resolved</dt><dd>{resolved.length}</dd></div>
        </dl>

        <section className="my-cases" aria-labelledby="my-cases-heading">
          <h2 id="my-cases-heading">My cases</h2>
          <div className="case-filters" aria-label="Filter cases">
            {(["all", "active", "attention", "resolved"] as Filter[]).map((item) => (
              <button key={item} type="button" aria-pressed={filter === item} onClick={() => setFilter(item)}>
                {item === "attention" ? "Needs attention" : item[0].toUpperCase() + item.slice(1)}
              </button>
            ))}
          </div>
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          {loading ? <p className="loading-row" role="status"><RefreshCw aria-hidden="true" /> Loading your demo cases…</p> : null}
          {!loading && !filtered.length ? (
            <div className="command-empty"><FolderOpen aria-hidden="true" /><h3>No cases in this view</h3><p>The Compose seed service adds eight synthetic walkthrough cases.</p><Link className="button button-primary" to="/file">File a simulated complaint</Link></div>
          ) : (
            <div className="case-table-wrap">
              <table className="case-table">
                <caption className="sr-only">Citizen complaint cases</caption>
                <thead><tr><th>Agency</th><th>Tracking ID</th><th>Status</th><th>Next action</th><th>Last updated</th><th><span className="sr-only">Action</span></th></tr></thead>
                <tbody>
                  {filtered.map((item) => {
                    const needsAttention = ["needs_attention", "retrying", "escalated"].includes(item.status);
                    const resolvedCase = item.status === "resolved";
                    const StatusIcon = needsAttention ? AlertTriangle : resolvedCase ? CheckCircle2 : CircleDot;
                    return <tr key={item.tracking_id}>
                      <td><strong>{item.agency.toUpperCase()}</strong><small>{agencyNames[item.agency] ?? item.agency}</small></td>
                      <td><code>{item.tracking_id}</code></td>
                      <td><span className={`status-text status-${item.status}`}><StatusIcon aria-hidden="true" />{labels[item.status] ?? item.status}</span><small>{item.retry_count ? `${item.retry_count} retry attempt` : item.complaint_type}</small></td>
                      <td><CalendarDays aria-hidden="true" /> {date(item.next_action_at)}</td>
                      <td>{date(item.last_updated)}</td>
                      <td>{needsAttention ? <button className="table-action primary" type="button" onClick={() => retry(item.tracking_id)} disabled={retrying === item.tracking_id}>{retrying === item.tracking_id ? "Retrying…" : "Retry"}</button> : <Link className="table-action" to={`/track?id=${encodeURIComponent(item.tracking_id)}`}>View case <ArrowRight aria-hidden="true" /></Link>}</td>
                    </tr>;
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>

      <aside className="command-rail" aria-label="Upcoming actions and demo status">
        <section className="upcoming-actions">
          <h2>Upcoming actions</h2>
          <ol>
            {attention.slice(0, 3).map((item, index) => <li key={item.tracking_id} className={index === 0 ? "overdue" : ""}><Clock3 aria-hidden="true" /><div><small>{index === 0 ? "Overdue" : date(item.next_action_at)}</small><strong>{labels[item.status]}</strong><span>{item.tracking_id}</span></div><Link to={`/track?id=${encodeURIComponent(item.tracking_id)}`}>Review</Link></li>)}
          </ol>
          <Link to="/track">View full timeline <ArrowRight aria-hidden="true" /></Link>
        </section>
        <section className="demo-disclosure"><ShieldCheck aria-hidden="true" /><div><h2>Demo environment</h2><p>Agency interactions shown here are simulated unless explicitly identified otherwise.</p></div></section>
        <section className="telemetry-strip"><h2>Simulated demo telemetry</h2><dl><div><dt>Queue</dt><dd><strong>8</strong><small>Normal</small></dd></div><div><dt>Wait</dt><dd><strong>1.4s</strong><small>Healthy</small></dd></div><div><dt>Success</dt><dd><strong>97.2%</strong><small>Demo data</small></dd></div></dl><a href="http://localhost:3000/d/citizen-karen-overview" target="_blank" rel="noreferrer">Open Grafana <ArrowRight aria-hidden="true" /></a></section>
      </aside>
    </div>
  );
}
