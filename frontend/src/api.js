// frontend/src/api.js
const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000/api";

export async function submitComplaint(data) {
  const resp = await fetch(`${API_BASE}/complaints`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!resp.ok) throw new Error("Submission failed");
  return resp.json();
}

export async function getStatus(trackingId) {
  const resp = await fetch(`${API_BASE}/complaints/${trackingId}`);
  if (!resp.ok) throw new Error("Not found");
  return resp.json();
}
