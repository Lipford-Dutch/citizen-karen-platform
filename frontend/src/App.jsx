// frontend/src/App.jsx
import React, { useState } from "react";
import ComplaintForm from "./components/ComplaintForm";
import StatusLookup from "./components/StatusLookup";
import "./index.css";

function App() {
  const [view, setView] = useState("submit");
  const [trackingId, setTrackingId] = useState(null);

  const handleSubmitted = (id) => {
    setTrackingId(id);
    setView("status");
  };

  return (
    <div className="container">
      <h1>Karing USA</h1>
      <nav aria-label="Main navigation">
        <button
          onClick={() => setView("submit")}
          aria-current={view === "submit" ? "page" : undefined}
        >
          Submit a Complaint
        </button>
        <button
          onClick={() => setView("status")}
          aria-current={view === "status" ? "page" : undefined}
        >
          Check Status
        </button>
      </nav>

      {view === "submit" && (
        <section aria-labelledby="submit-heading">
          <h2 id="submit-heading">Submit a Complaint</h2>
          <ComplaintForm onSubmitted={handleSubmitted} />
        </section>
      )}

      {view === "status" && (
        <section aria-labelledby="status-heading">
          <h2 id="status-heading">Check Complaint Status</h2>
          {trackingId && (
            <p>Your tracking ID is <strong>{trackingId}</strong></p>
          )}
          <StatusLookup initialId={trackingId} />
        </section>
      )}
    </div>
  );
}

export default App;
