// Backend API client. Always calls relative `/api/...` (dev proxy / Vercel rewrite).
import type {
  AnalysisRequest, AnalysisResponse, AuditEntry, DemoConfig, DrugDetail, DrugSummary,
  LabTrendAssessment, LabTrendRequest,
} from "./types";

/** `message` is safe to show to people; `detail` is the technical text behind "View details". */
export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, message: string, detail = "") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function detailToString(d: unknown): string {
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((e) => (e && typeof e === "object" && "msg" in e ? String((e as { msg: unknown }).msg) : JSON.stringify(e)))
      .join("; ");
  }
  return "";
}

function friendlyFor(status: number, detail: string): string {
  if (status === 0) return "The safety service could not be reached. Check that the backend is running, then try again.";
  if (status === 404) return detail || "That item was not found.";
  if (status === 400 || status === 422) return detail || "Some of the information entered could not be processed.";
  if (status >= 500) return "The safety service ran into a problem and could not finish. Try again in a moment.";
  return detail || "The request could not be completed.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...init });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ApiError(0, friendlyFor(0, ""), "Network error: the request did not reach the server.");
  }
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = detailToString(body?.detail ?? body);
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, friendlyFor(res.status, detail), `HTTP ${res.status} ${res.statusText}${detail ? ` — ${detail}` : ""}`);
  }
  return (await res.json()) as T;
}

/** engine/audit.py owns the raw record shape, so read it defensively. */
function normalizeAudit(raw: unknown, i: number): AuditEntry {
  const r = (raw && typeof raw === "object" ? raw : {}) as Record<string, unknown>;
  const pick = (...keys: string[]) => keys.map((k) => r[k]).find((v) => v !== undefined);
  const drugs = pick("drugs", "drug_ids", "drugs_analyzed");
  const patient = pick("patient_context_provided", "patient_provided", "patientProvided");
  return {
    id: String(pick("audit_id", "id") ?? `record-${i}`),
    timestamp: String(pick("timestamp", "ts", "time", "created_at") ?? ""),
    drugs: Array.isArray(drugs) ? drugs.map(String) : [],
    patientProvided: typeof patient === "boolean" ? patient : null,
    demo: Boolean(pick("demo_mode", "demo")),
  };
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  searchDrugs: (q: string, signal?: AbortSignal, limit = 10) =>
    request<DrugSummary[]>(`/api/drugs?q=${encodeURIComponent(q)}&limit=${limit}`, { signal }),
  drug: (id: string) => request<DrugDetail>(`/api/drugs/${encodeURIComponent(id)}`),
  demo: () => request<DemoConfig>("/api/demo"),
  analyze: (body: AnalysisRequest) =>
    request<AnalysisResponse>("/api/analyze", { method: "POST", body: JSON.stringify(body) }),
  labTrend: (body: LabTrendRequest) =>
    request<LabTrendAssessment>("/api/lab-trend", { method: "POST", body: JSON.stringify(body) }),
  audit: async (limit = 20): Promise<AuditEntry[]> => {
    const rows = await request<unknown[]>(`/api/audit?limit=${limit}`);
    return Array.isArray(rows) ? rows.map(normalizeAudit) : [];
  },
};
