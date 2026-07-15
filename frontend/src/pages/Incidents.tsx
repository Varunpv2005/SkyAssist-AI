import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  Shield,
  Clock,
  CheckCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { incidentsApi, ApiError } from "../services/api";
import type { Incident, IncidentLevel, IncidentStatus } from "../types";

const SEVERITY_STYLES: Record<IncidentLevel, string> = {
  Critical: "bg-red-500/20 text-red-400 border-red-500/40",
  High: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  Medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  Low: "bg-sky-500/15 text-sky-400 border-sky-500/30",
};

const STATUS_STYLES: Record<IncidentStatus, string> = {
  open: "bg-red-500/15 text-red-400",
  investigating: "bg-amber-500/15 text-amber-400",
  resolved: "bg-emerald-500/15 text-emerald-400",
  closed: "bg-gray-500/15 text-gray-400",
};

const ISSUE_LABELS: Record<string, string> = {
  AUTH_FAILURE: "Auth Failure",
  TOKEN_EXPIRED: "Token Expired",
  API_TIMEOUT: "API Timeout",
  DATABASE_CONNECTION_ERROR: "DB Connection",
  SSL_HANDSHAKE_FAILURE: "SSL Handshake",
  EMAIL_DELIVERY_FAILURE: "Email Delivery",
  NETWORK_ERROR: "Network Error",
  DNS_ERROR: "DNS Error",
};

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState({ total: 0, critical: 0, high: 0, open: 0, resolved: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [listData, statsData] = await Promise.all([
        incidentsApi.list(),
        incidentsApi.stats(),
      ]);
      setIncidents(listData.incidents);
      setStats(statsData);
    } catch {
      setError("Failed to load incidents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStatusUpdate = async (incidentId: string, status: IncidentStatus) => {
    setUpdatingId(incidentId);
    try {
      await incidentsApi.update(incidentId, { status });
      await fetchData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Update failed");
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-gray-100">Incident Detection</h2>
        <p className="mt-1 text-sm text-gray-400">
          Rule-based incidents detected from parsed security logs.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Total", value: stats.total, color: "text-sky-400" },
          { label: "Critical", value: stats.critical, color: "text-red-400" },
          { label: "Open", value: stats.open, color: "text-amber-400" },
          { label: "Resolved", value: stats.resolved, color: "text-emerald-400" },
        ].map((s) => (
          <div key={s.label} className="card-hover animate-fade-in">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-sm text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="card animate-fade-in">
        <div className="mb-4 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-sky-400" />
          <h3 className="text-base font-semibold text-gray-100">Detected Incidents</h3>
          <span className="ml-auto text-xs text-gray-500">{incidents.length} total</span>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
          </div>
        ) : incidents.length === 0 ? (
          <div className="py-12 text-center">
            <Shield className="mx-auto h-10 w-10 text-gray-600" />
            <p className="mt-3 text-sm text-gray-500">
              No incidents yet. Upload and parse logs to detect issues.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((incident) => {
              const isExpanded = expandedId === incident.incident_id;
              return (
                <div
                  key={incident.incident_id}
                  className="rounded-lg border border-surface-border bg-surface transition-colors hover:border-sky-500/30"
                >
                  <button
                    onClick={() =>
                      setExpandedId(isExpanded ? null : incident.incident_id)
                    }
                    className="flex w-full items-center gap-3 p-4 text-left"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-500/10">
                      <AlertTriangle className="h-4 w-4 text-red-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-sm font-semibold text-sky-400">
                          {incident.incident_id}
                        </span>
                        <span
                          className={`rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase ${SEVERITY_STYLES[incident.severity]}`}
                        >
                          {incident.severity}
                        </span>
                        <span className="rounded bg-surface-hover px-2 py-0.5 text-xs text-gray-400">
                          {ISSUE_LABELS[incident.issue_type] || incident.issue_type}
                        </span>
                        <span
                          className={`rounded px-2 py-0.5 text-xs font-medium capitalize ${STATUS_STYLES[incident.status]}`}
                        >
                          {incident.status}
                        </span>
                      </div>
                      <p className="mt-1 truncate text-sm text-gray-400">
                        {incident.description}
                      </p>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4 shrink-0 text-gray-500" />
                    ) : (
                      <ChevronDown className="h-4 w-4 shrink-0 text-gray-500" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="border-t border-surface-border px-4 pb-4 pt-3">
                      <div className="grid gap-3 sm:grid-cols-2">
                        <div>
                          <p className="text-xs font-medium uppercase text-gray-500">Root Cause</p>
                          <p className="mt-1 text-sm text-gray-300">{incident.root_cause}</p>
                        </div>
                        <div>
                          <p className="text-xs font-medium uppercase text-gray-500">Source</p>
                          <p className="mt-1 text-sm text-gray-300">{incident.source || "—"}</p>
                        </div>
                      </div>
                      <div className="mt-3">
                        <p className="text-xs font-medium uppercase text-gray-500">Recommendation</p>
                        <p className="mt-1 text-sm text-gray-300">{incident.recommendation}</p>
                      </div>
                      {incident.status === "open" && (
                        <div className="mt-4 flex gap-2">
                          <button
                            onClick={() => handleStatusUpdate(incident.incident_id, "investigating")}
                            disabled={updatingId === incident.incident_id}
                            className="btn-secondary text-xs"
                          >
                            <Clock className="h-3.5 w-3.5" />
                            Investigate
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(incident.incident_id, "resolved")}
                            disabled={updatingId === incident.incident_id}
                            className="btn-primary text-xs"
                          >
                            <CheckCircle className="h-3.5 w-3.5" />
                            Resolve
                          </button>
                        </div>
                      )}
                      {incident.status === "investigating" && (
                        <div className="mt-4 flex gap-2">
                          <button
                            onClick={() => handleStatusUpdate(incident.incident_id, "resolved")}
                            disabled={updatingId === incident.incident_id}
                            className="btn-primary text-xs"
                          >
                            <CheckCircle className="h-3.5 w-3.5" />
                            Resolve
                          </button>
                        </div>
                      )}
                      {incident.status === "resolved" && (
                        <div className="mt-4 flex gap-2">
                          <button
                            onClick={() => handleStatusUpdate(incident.incident_id, "closed")}
                            disabled={updatingId === incident.incident_id}
                            className="btn-secondary text-xs"
                          >
                            Close
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
