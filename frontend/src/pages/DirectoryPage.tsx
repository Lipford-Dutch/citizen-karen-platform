import {
  ArrowRight,
  BadgeDollarSign,
  ExternalLink,
  Landmark,
  Leaf,
  Search,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { type FormEvent, useDeferredValue, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import wayfinding from "../assets/civic-wayfinding.png";
import {
  type AgencyCategory,
  type AgencyDestination,
  searchAgencies,
} from "../data/agencies";


const categoryIcons = {
  Consumer: BadgeDollarSign,
  "Civil rights": Landmark,
  Safety: ShieldCheck,
  Health: ShieldCheck,
  Government: Landmark,
  Environment: Leaf,
} satisfies Record<AgencyCategory, typeof ShieldCheck>;

const featuredSlugs = new Set(["fcc", "cfpb", "doj-civil-rights", "osha", "epa", "ftc"]);

function DestinationLink({ agency }: { agency: AgencyDestination }) {
  const Icon = categoryIcons[agency.category];
  const content = (
    <>
      <span className="destination-icon" aria-hidden="true">
        <Icon />
      </span>
      <span className="destination-copy">
        <strong>{agency.title}</strong>
        <span>{agency.description}</span>
        <small>{agency.agency}</small>
      </span>
      {agency.direct ? (
        <ArrowRight className="destination-arrow" aria-hidden="true" />
      ) : (
        <ExternalLink className="destination-arrow" aria-hidden="true" />
      )}
    </>
  );

  return agency.direct ? (
    <Link className="destination-row" to="/file">
      {content}
      <span className="sr-only">File inside Citizen Karen</span>
    </Link>
  ) : (
    <a
      className="destination-row"
      href={agency.officialUrl}
      target="_blank"
      rel="noreferrer"
    >
      {content}
      <span className="sr-only">Opens the official website in a new tab</span>
    </a>
  );
}

export function DirectoryPage() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const results = useMemo(() => searchAgencies(deferredQuery), [deferredQuery]);
  const directoryRef = useRef<HTMLElement>(null);
  const featured = useMemo(
    () => results.filter((agency) => featuredSlugs.has(agency.slug)),
    [results],
  );
  const remaining = useMemo(
    () => results.filter((agency) => !featuredSlugs.has(agency.slug)),
    [results],
  );

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    directoryRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <>
      <section className="hero page-width" aria-labelledby="directory-heading">
        <div className="hero-copy">
          <h1 id="directory-heading">One clear path to the right public agency.</h1>
          <p>
            Find the official destination, file an FCC complaint, or pick up where
            you left off.
          </p>
          <form className="agency-search" role="search" onSubmit={handleSearch}>
            <label className="sr-only" htmlFor="agency-query">
              Describe what happened
            </label>
            <Search aria-hidden="true" />
            <input
              id="agency-query"
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={'What happened? Try “robocalls” or “unsafe workplace”'}
              autoComplete="off"
            />
          </form>
          <div className="hero-actions">
            <button className="button button-primary" type="button" onClick={() => directoryRef.current?.scrollIntoView({ behavior: "smooth" })}>
              <Search aria-hidden="true" />
              Find an agency
              <ArrowRight aria-hidden="true" />
            </button>
            <Link className="button button-secondary" to="/track">
              <Landmark aria-hidden="true" />
              Track a case
              <ArrowRight aria-hidden="true" />
            </Link>
          </div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <img src={wayfinding} alt="" width="768" height="512" />
        </div>
      </section>

      <section className="directory-section page-width" ref={directoryRef} aria-labelledby="destinations-heading">
        <div className="section-heading-row">
          <div>
            <h2 id="destinations-heading">
              {query ? "Matching official destinations" : "Featured official destinations"}
            </h2>
            <p aria-live="polite">
              {results.length} {results.length === 1 ? "destination" : "destinations"}
              {query ? ` for “${query}”` : " in the repository directory"}.
            </p>
          </div>
          <span className="directory-source">Official sites open in a new tab</span>
        </div>

        {results.length ? (
          <>
            <div className="destination-grid" data-testid="featured-destinations">
              {(query ? results.slice(0, 8) : featured).map((agency) => (
                <DestinationLink agency={agency} key={agency.slug} />
              ))}
            </div>
            {!query && remaining.length > 0 ? (
              <details className="all-destinations">
                <summary>Browse all {results.length} destinations</summary>
                <div className="destination-grid destination-grid-all">
                  {remaining.map((agency) => (
                    <DestinationLink agency={agency} key={agency.slug} />
                  ))}
                </div>
              </details>
            ) : null}
          </>
        ) : (
          <div className="empty-state" role="status">
            <TriangleAlert aria-hidden="true" />
            <div>
              <h3>No close match yet</h3>
              <p>Try a shorter phrase such as “housing,” “bank,” “work,” or “fraud.”</p>
            </div>
          </div>
        )}
      </section>

      <aside className="trust-band" aria-label="Privacy commitment">
        <div className="page-width trust-inner">
          <ShieldCheck aria-hidden="true" />
          <div>
            <strong>Clear consent. Minimal data. Official destinations.</strong>
            <span>
              You’re in control. We collect only what is needed for direct filing and
              route every other issue to an official agency website.
            </span>
          </div>
          <Link to="/privacy">
            Learn more about privacy <ArrowRight aria-hidden="true" />
          </Link>
        </div>
      </aside>
    </>
  );
}
