import type {
  AuthToken,
  LoginCredentials,
  LogListResponse,
  LogUploadResponse,
  ParseLogResponse,
  RegisterData,
  IncidentListResponse,
  IncidentStats,
  Incident,
  RCAAnalysis,
  RCAListResponse,
  AIResponse,
  AIHistoryResponse,
  AIAskRequest,
  Ticket,
  TicketListResponse,
  TicketStats,
  TicketCreateRequest,
  Alert,
  AlertListResponse,
  AlertStats,
  AnalyticsData,
  AnalyticsPeriod,
  SearchScope,
  SearchResponse,
  KnowledgeArticle,
  Remediation,
  User,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("skyassist_token");

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("skyassist_token");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    const message =
      typeof error.detail === "string"
        ? error.detail
        : Array.isArray(error.detail)
          ? error.detail.map((e: { msg: string }) => e.msg).join(", ")
          : "Request failed";
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  if (!text) {
    return undefined as T;
  }

  return JSON.parse(text) as T;
}

async function uploadRequest<T>(
  endpoint: string,
  formData: FormData,
): Promise<T> {
  const token = localStorage.getItem("skyassist_token");
  const headers: HeadersInit = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    const message =
      typeof error.detail === "string" ? error.detail : "Upload failed";
    throw new ApiError(message, response.status);
  }

  return response.json();
}

export const authApi = {
  login: (credentials: LoginCredentials) =>
    request<AuthToken>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    }),

  register: (data: RegisterData) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getMe: () => request<User>("/auth/me"),
};

export const logsApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return uploadRequest<LogUploadResponse>("/logs/upload", formData);
  },

  list: () => request<LogListResponse>("/logs"),

  parse: (logId: number) =>
    request<ParseLogResponse>(`/logs/${logId}/parse`, { method: "POST" }),

  getEntries: (logId: number) =>
    request<ParseLogResponse>(`/logs/${logId}/entries`),
};

export const incidentsApi = {
  list: () => request<IncidentListResponse>("/incidents"),

  stats: () => request<IncidentStats>("/incidents/stats"),

  get: (incidentId: string) => request<Incident>(`/incidents/${incidentId}`),

  detect: (logId: number) =>
    request<{ incidents_detected: number }>(`/incidents/detect/${logId}`, {
      method: "POST",
    }),

  update: (incidentId: string, data: { status: string }) =>
    request<Incident>(`/incidents/${incidentId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

export const analysisApi = {
  list: () => request<RCAListResponse>("/analysis"),

  analyze: (incidentId: string) =>
    request<{ analysis: RCAAnalysis }>(`/analysis/incident/${incidentId}`, {
      method: "POST",
    }),

  get: (incidentId: string) =>
    request<RCAAnalysis>(`/analysis/incident/${incidentId}`),
};

export const aiApi = {
  ask: (data: AIAskRequest) =>
    request<AIResponse>("/ai/ask", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  history: () => request<AIHistoryResponse>("/ai/history"),

  status: () =>
    request<{ available: boolean; model: string; message?: string }>("/ai/status"),

  remediate: (data: { incident_id?: string; log_snippet?: string; context?: string }) =>
    request<Remediation>("/ai/remediate", { method: "POST", body: JSON.stringify(data) }),

  remediations: () =>
    request<{ total: number; remediations: Remediation[] }>("/ai/remediations"),

  knowledgeRetrieve: (q: string) =>
    request<{ total: number; articles: { article_id: string; title: string; category: string; tags: string[] }[] }>(
      `/ai/knowledge?q=${encodeURIComponent(q)}`,
    ),
};

export const ticketsApi = {
  list: () => request<TicketListResponse>("/tickets"),

  stats: () => request<TicketStats>("/tickets/stats"),

  get: (ticketId: string) => request<Ticket>(`/tickets/${ticketId}`),

  create: (data: TicketCreateRequest) =>
    request<Ticket>("/tickets", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (
    ticketId: string,
    data: Partial<{
      issue: string;
      priority: string;
      root_cause: string;
      assigned_to: string;
      status: string;
    }>,
  ) =>
    request<Ticket>(`/tickets/${ticketId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (ticketId: string) =>
    request<void>(`/tickets/${ticketId}`, { method: "DELETE" }),
};

export const alertsApi = {
  list: () => request<AlertListResponse>("/alerts"),

  stats: () => request<AlertStats>("/alerts/stats"),

  markRead: (alertId: string) =>
    request<Alert>(`/alerts/${alertId}/read`, { method: "PATCH" }),

  markAllRead: () =>
    request<{ marked_read: number }>("/alerts/read-all", { method: "POST" }),
};

export const analyticsApi = {
  get: (period: AnalyticsPeriod = "daily") =>
    request<AnalyticsData>(`/analytics?period=${period}`),
};

export const searchApi = {
  search: (params: {
    q?: string;
    scope?: SearchScope;
    severity?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }) => {
    const sp = new URLSearchParams();
    if (params.q) sp.set("q", params.q);
    if (params.scope) sp.set("scope", params.scope);
    if (params.severity) sp.set("severity", params.severity);
    if (params.status) sp.set("status", params.status);
    if (params.page) sp.set("page", String(params.page));
    if (params.page_size) sp.set("page_size", String(params.page_size));
    return request<SearchResponse>(`/search?${sp.toString()}`);
  },
};

export const knowledgeApi = {
  list: (category?: string) =>
    request<{ total: number; articles: KnowledgeArticle[] }>(
      category ? `/knowledge?category=${encodeURIComponent(category)}` : "/knowledge",
    ),
  get: (id: string) => request<KnowledgeArticle>(`/knowledge/${id}`),
  create: (data: {
    title: string;
    content: string;
    category: string;
    tags?: string[];
    incident_id?: string;
    rca_id?: number;
  }) => request<KnowledgeArticle>("/knowledge", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<{ title: string; content: string; category: string; tags: string[] }>) =>
    request<KnowledgeArticle>(`/knowledge/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/knowledge/${id}`, { method: "DELETE" }),
  search: (q: string) =>
    request<{ total: number; articles: KnowledgeArticle[] }>(`/knowledge/search?q=${encodeURIComponent(q)}`),
};

export { ApiError };
