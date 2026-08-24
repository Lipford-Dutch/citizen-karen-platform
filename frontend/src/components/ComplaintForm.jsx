// frontend/src/components/ComplaintForm.jsx
import React, { useState } from "react";
import { submitComplaint } from "../api";

export default function ComplaintForm({ onSubmitted }) {
  const [form, setForm] = useState({ name: "", email: "", description: "", agency_hint: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await submitComplaint(form);
      onSubmitted(res.tracking_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} aria-label="Complaint submission form">
      <label>
        Your name
        <input name="name" value={form.name} onChange={handleChange} required />
      </label>
      <label>
        Your email
        <input name="email" type="email" value={form.email} onChange={handleChange} required />
      </label>
      <label>
        Complaint description
        <textarea name="description" rows="5" value={form.description} onChange={handleChange} required />
      </label>
      <label>
        Agency hint (optional)
        <input name="agency_hint" value={form.agency_hint} onChange={handleChange} />
      </label>
      <button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Submit Complaint"}
      </button>
      {error && <p role="alert" style={{ color: "red" }}>{error}</p>}
    </form>
  );
}
