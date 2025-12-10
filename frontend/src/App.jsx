// frontend/src/App.jsx
import React, { useState } from "react";
import ComplaintForm from "./components/ComplaintForm";
import StatusLookup from "./components/StatusLookup";
import "./index.css";

function App() {
  const [trackingId, setTrackingId] = useState(null);

  return (
    <div className="container">
      <h1>Karing USA — Submit a Complaint</h1>
      {!trackingId ? (
        <ComplaintForm onSubmitted={setTrackingId} />
      ) : (
        <div>
          <p>Thank you! Your tracking ID is <strong>{trackingId}</strong></p>
          <StatusLookup />
        </div>
      )}
    </div>
  );
}

export default App;
