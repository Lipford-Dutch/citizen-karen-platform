import { FlaskConical, Menu, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

import brandMark from "../assets/brand-mark.jpg";
import { ScrollToTop } from "./ScrollToTop";


const navigation = [
  { label: "Command Center", to: "/" },
  { label: "Find an agency", to: "/directory" },
  { label: "File a complaint", to: "/file" },
  { label: "Track a case", to: "/track" },
  { label: "Admin demo", to: "/admin" },
];

export function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="app-shell">
      <ScrollToTop />
      <header className="site-header">
        <div className="page-width header-inner">
          <Link className="brand" to="/" aria-label="Citizen Karen home">
            <img src={brandMark} alt="" width="92" height="64" />
            <span className="brand-copy">
              <strong>Citizen Karen</strong>
              <span>Karing USA</span>
            </span>
          </Link>
          <button
            className="mobile-menu-button"
            type="button"
            aria-expanded={menuOpen}
            aria-controls="main-navigation"
            aria-label={menuOpen ? "Close navigation" : "Open navigation"}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
          </button>
          <nav
            id="main-navigation"
            className={menuOpen ? "main-navigation is-open" : "main-navigation"}
            aria-label="Main navigation"
          >
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                onClick={() => setMenuOpen(false)}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <span className="demo-mode"><FlaskConical aria-hidden="true" /> Demo mode</span>
        </div>
      </header>

      <main id="main-content">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="page-width footer-inner">
          <nav aria-label="Footer navigation">
            <Link to="/privacy">Privacy</Link>
            <Link to="/accessibility">Accessibility</Link>
            <Link to="/security">Security</Link>
            <a
              href="https://github.com/Lipford-Dutch/citizen-karen-platform"
              rel="noreferrer"
              target="_blank"
            >
              GitHub
            </a>
          </nav>
          <strong className="footer-disclaimer">Not a government service or legal advice.</strong>
          <Link className="footer-brand" to="/" aria-label="Citizen Karen home">
            <img src={brandMark} alt="" width="68" height="48" />
            <span>
              <strong>Citizen Karen</strong>
              <small>Karing USA</small>
            </span>
          </Link>
        </div>
      </footer>
    </div>
  );
}
