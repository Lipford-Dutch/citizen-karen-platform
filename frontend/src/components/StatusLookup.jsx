// frontend/src/components/StatusLookup.jsx
import React, { useState } from "react";
import { getStatus } from "../api";

export default function StatusLookup({ initialId = "" }) {
  const [trackingId, setTrackingId] = useState(initialId);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleCheck = async (e) => {
    e.preventDefault();
    setError(null);
    setStatus(null);
    try {
      const res = await getStatus(trackingId);
      setStatus(res);
    } catch (err) {
      setError("Could not find status for that ID.");
    }
  };

  return (
    <div>
      <form onSubmit={handleCheck} aria-label="Check complaint status">
        <label>
          Tracking ID
          <input value={trackingId} onChange={e => setTrackingId(e.target.value)} required />
        </label>
        <button type="submit">Check Status</button>
      </form>
      {error && <p role="alert" style={{ color: "red" }}>{error}</p>}
      {status && (
        <div aria-live="polite">
          <p><strong>Status:</strong> {status.status}</p>
          <p><strong>Agency:</strong> {status.agency || "Not yet routed"}</p>
          <p><strong>Submitted at:</strong> {new Date(status.submitted_at).toLocaleString()}</p>
          <p><strong>Last updated:</strong> {new Date(status.last_updated).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}
