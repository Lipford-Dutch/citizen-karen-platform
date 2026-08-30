const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export type ComplaintInput = {
  agency: string;
  full_name: string;
  email: string;
  phone_number: string;
  complaint_type: string;
  description: string;
  consent: boolean;
  consent_version: "2026-08-23";
  website: string;
  dynamic_fields?: Record<string, string | boolean | number | null>;
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
  events?: Array<{ type: string; occurred_at: string; metadata: Record<string, unknown> }>;
  retry_count?: number;
  next_action_at?: string | null;
};

export type PluginManifest = {
  key: string;
  name: string;
  short_name: string;
  description: string;
  official_url: string;
  category: string;
  risk_score: number;
  risk_level: string;
  automation: string;
  simulated: boolean;
  kyc_level: string;
  restrictions: string[];
  form_schema: DynamicSchema;
};

export type DynamicField = {
  type: "string" | "boolean";
  title: string;
  format?: string;
  minLength?: number;
  maxLength?: number;
  enum?: string[];
  step?: string;
};

export type DynamicSchema = {
  title: string;
  type: "object";
  required: string[];
  properties: Record<string, DynamicField>;
};

export type CaseSummary = {
  id: string;
  tracking_id: string;
  agency: string;
  agency_reference: string | null;
  complaint_type: string;
  status: string;
  submitted_at: string;
  last_updated: string;
  next_action_at: string | null;
  retry_count: number;
};

const TOKEN_KEY = "citizen-karen-demo-token";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = sessionStorage.getItem(TOKEN_KEY);
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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

export async function demoLogin(role: "citizen" | "admin" | "anonymous" = "citizen") {
  const result = await request<{ access_token: string; user: { name: string; role: string } }>(`/auth/demo/${role}`, { method: "POST" });
  sessionStorage.setItem(TOKEN_KEY, result.access_token);
  return result.user;
}

export function getPlugins(): Promise<{ plugins: PluginManifest[]; disclaimer: string }> {
  return request("/plugins");
}

export function getCases(): Promise<{ cases: CaseSummary[]; disclaimer: string }> {
  return request("/complaints");
}

export function retryComplaint(trackingId: string): Promise<{ state: string }> {
  return request(`/complaints/${encodeURIComponent(trackingId)}/retry`, { method: "POST" });
}

export async function uploadEvidence(trackingId: string, file: File): Promise<{ scan_status: string; retention_days: number }> {
  const form = new FormData();
  form.append("evidence", file);
  const token = sessionStorage.getItem(TOKEN_KEY);
  const response = await fetch(`${API_BASE}/complaints/${encodeURIComponent(trackingId)}/evidence`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(payload?.detail ?? "Evidence upload failed");
  }
  return response.json() as Promise<{ scan_status: string; retention_days: number }>;
}

export function getAdminOperations(): Promise<{ counts: Record<string, number>; queue: { mode: string; status: string } }> {
  return request("/admin/operations");
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
