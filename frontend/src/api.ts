const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export type ComplaintInput = {
  agency: "fcc";
  full_name: string;
  email: string;
  phone_number: string;
  complaint_type: string;
  description: string;
  consent: boolean;
  consent_version: "2026-08-23";
  website: string;
};

export type ComplaintReceipt = {
  id: string;
  tracking_id: string;
  received: boolean;
  state: string;
  agency: string;
  agency_reference: string | null;
  submitted_at: string;
};

export type ComplaintStatus = {
  id: string;
  tracking_id: string;
  state: string;
  agency: string;
  agency_reference: string | null;
  complaint_type: string;
  submitted_at: string;
  last_updated: string;
  consent_version: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { detail?: string | Array<{ msg?: string }> }
      | null;
    const detail = Array.isArray(payload?.detail)
      ? payload.detail.map((item) => item.msg).filter(Boolean).join(" ")
      : payload?.detail;
    throw new Error(detail || "Something went wrong. Please try again.");
  }

  return response.json() as Promise<T>;
}

export function submitComplaint(data: ComplaintInput): Promise<ComplaintReceipt> {
  return request<ComplaintReceipt>("/complaints", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getComplaintStatus(trackingId: string): Promise<ComplaintStatus> {
  return request<ComplaintStatus>(`/complaints/${encodeURIComponent(trackingId)}`);
}

export function deleteComplaintCopy(
  trackingId: string,
): Promise<{ tracking_id: string; state: string; message: string }> {
  return request(`/complaints/${encodeURIComponent(trackingId)}`, {
    method: "DELETE",
  });
}
