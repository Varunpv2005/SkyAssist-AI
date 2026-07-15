export type UserRole = "admin" | "analyst" | "user";

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  role?: UserRole;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export type LogStatus = "uploaded" | "processing" | "parsed" | "failed";

export interface LogFile {
  id: number;
  filename: string;
  file_size: number;
  file_type: string;
  status: LogStatus;
  uploaded_by: number;
  created_at: string;
}

export interface LogUploadResponse extends LogFile {
  message: string;
}

export interface LogListResponse {
  total: number;
  logs: LogFile[];
}

export type EntrySeverity = "CRITICAL" | "ERROR" | "WARNING" | "INFO" | "DEBUG" | "UNKNOWN";

export interface ParsedEntry {
  id: number;
  timestamp: string | null;
  severity: EntrySeverity;
  message: string;
  source: string | null;
  line_number: number;
}

export interface ParseLogResponse {
  log_file_id: number;
  filename: string;
  total_entries: number;
  entries: ParsedEntry[];
  severity_summary: Record<string, number>;
  message: string;
}

export type IssueType =
  | "AUTH_FAILURE"
  | "TOKEN_EXPIRED"
  | "API_TIMEOUT"
  | "DATABASE_CONNECTION_ERROR"
  | "SSL_HANDSHAKE_FAILURE"
  | "EMAIL_DELIVERY_FAILURE"
  | "NETWORK_ERROR"
  | "DNS_ERROR";

export type IncidentLevel = "Critical" | "High" | "Medium" | "Low";
export type IncidentStatus = "open" | "investigating" | "resolved" | "closed";

export interface Incident {
  id: number;
  incident_id: string;
  issue_type: IssueType;
  severity: IncidentLevel;
  root_cause: string;
  description: string;
  recommendation: string;
  status: IncidentStatus;
  source: string | null;
  log_file_id: number | null;
  log_entry_id: number | null;
  created_at: string;
}

export interface IncidentListResponse {
  total: number;
  incidents: Incident[];
}

export interface IncidentStats {
  total: number;
  critical: number;
  high: number;
  open: number;
  resolved: number;
}

export interface RCAAnalysis {
  id: number;
  incident_id: number;
  incident_ref: string;
  issue: string;
  possible_causes: string[];
  recommended_action: string;
  confidence_score: number;
  created_at: string;
}

export interface RCAListResponse {
  total: number;
  analyses: RCAAnalysis[];
}

export interface AIResponse {
  id: number;
  root_cause: string;
  explanation: string;
  resolution_steps: string[];
  confidence_score: number;
  source: string;
  question: string;
  created_at: string;
}

export interface AIHistoryResponse {
  total: number;
  history: AIResponse[];
}

export interface AIAskRequest {
  question: string;
  log_snippet?: string;
  incident_id?: string;
  severity?: string;
}

export type TicketPriority = "Critical" | "High" | "Medium" | "Low";
export type TicketStatus = "open" | "in_progress" | "resolved" | "closed";

export interface Ticket {
  id: number;
  ticket_id: string;
  issue: string;
  priority: TicketPriority;
  root_cause: string;
  assigned_to: string | null;
  status: TicketStatus;
  incident_id: number | null;
  incident_ref: string | null;
  created_by: number;
  created_at: string;
}

export interface TicketListResponse {
  total: number;
  tickets: Ticket[];
}

export interface TicketStats {
  total: number;
  open: number;
  in_progress: number;
  resolved: number;
  closed: number;
}

export type AlertSeverity = "critical" | "high" | "medium" | "low" | "info";
export type AlertType = "incident" | "ticket" | "system";

export interface Alert {
  id: number;
  alert_id: string;
  title: string;
  message: string;
  severity: AlertSeverity;
  alert_type: AlertType;
  reference_id: string | null;
  is_read: boolean;
  created_at: string;
}

export interface AlertListResponse {
  total: number;
  unread: number;
  alerts: Alert[];
}

export interface AlertStats {
  total: number;
  unread: number;
  critical: number;
}

export interface TicketCreateRequest {
  issue: string;
  priority: TicketPriority;
  root_cause: string;
  assigned_to?: string;
  incident_id?: string;
}

export type AnalyticsPeriod = "daily" | "weekly" | "monthly";

export interface TrendPoint {
  label: string;
  count: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface NameValue {
  name: string;
  value: number;
}

export interface AnalyticsData {
  period: AnalyticsPeriod;
  incident_trends: TrendPoint[];
  severity_distribution: NameValue[];
  top_error_categories: CategoryCount[];
  resolved_vs_unresolved: NameValue[];
  alert_frequency: TrendPoint[];
  ticket_status: NameValue[];
  summary: Record<string, number>;
}

export interface DashboardStat {
  label: string;
  value: number;
  change: number;
  trend: "up" | "down" | "neutral";
  icon: string;
  color: "sky" | "red" | "green" | "amber" | "purple";
}

export interface ActivityItem {
  id: string;
  type: "incident" | "ticket" | "alert" | "log";
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  timestamp: string;
}

export type SearchScope = "all" | "incidents" | "logs" | "tickets" | "ai" | "knowledge";

export interface SearchHit {
  type: string;
  id: string;
  title: string;
  subtitle?: string;
  severity?: string;
  status?: string;
  created_at: string;
  link: string;
}

export interface SearchResponse {
  scope: SearchScope;
  query?: string;
  total: number;
  page: number;
  page_size: number;
  pages: number;
  results: SearchHit[];
}

export interface KnowledgeArticle {
  id: number;
  article_id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  incident_id: number | null;
  incident_ref: string | null;
  rca_id: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface Remediation {
  id: number;
  remediation_id: string;
  incident_ref: string | null;
  recommended_fixes: string[];
  troubleshooting_steps: string[];
  confidence_score: number;
  source: string;
  created_at: string;
}
