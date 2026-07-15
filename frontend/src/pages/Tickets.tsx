import { useCallback, useEffect, useState } from "react";
import {
  Ticket,
  Plus,
  Loader2,
  ChevronDown,
  ChevronUp,
  Trash2,
  User,
  Clock,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { ticketsApi, ApiError } from "../services/api";
import type { Ticket as TicketType, TicketPriority, TicketStatus } from "../types";

const PRIORITY_STYLES: Record<TicketPriority, string> = {
  Critical: "bg-red-500/20 text-red-400 border-red-500/40",
  High: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  Medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  Low: "bg-sky-500/15 text-sky-400 border-sky-500/30",
};

const STATUS_STYLES: Record<TicketStatus, string> = {
  open: "bg-red-500/15 text-red-400",
  in_progress: "bg-amber-500/15 text-amber-400",
  resolved: "bg-emerald-500/15 text-emerald-400",
  closed: "bg-gray-500/15 text-gray-400",
};

const STATUS_LABELS: Record<TicketStatus, string> = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
  closed: "Closed",
};

export default function Tickets() {
  const [tickets, setTickets] = useState<TicketType[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    in_progress: 0,
    resolved: 0,
    closed: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    issue: "",
    priority: "Medium" as TicketPriority,
    root_cause: "",
    assigned_to: "",
  });

  const fetchData = useCallback(async () => {
    try {
      const [listData, statsData] = await Promise.all([
        ticketsApi.list(),
        ticketsApi.stats(),
      ]);
      setTickets(listData.tickets);
      setStats(statsData);
    } catch {
      setError("Failed to load tickets");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStatusUpdate = async (ticketId: string, status: TicketStatus) => {
    setUpdatingId(ticketId);
    try {
      await ticketsApi.update(ticketId, { status });
      await fetchData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Update failed");
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDelete = async (ticketId: string) => {
    setUpdatingId(ticketId);
    try {
      await ticketsApi.delete(ticketId);
      await fetchData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    } finally {
      setUpdatingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError("");
    try {
      await ticketsApi.create({
        issue: form.issue,
        priority: form.priority,
        root_cause: form.root_cause,
        assigned_to: form.assigned_to || undefined,
      });
      setForm({ issue: "", priority: "Medium", root_cause: "", assigned_to: "" });
      setShowCreate(false);
      await fetchData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Create failed");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="animate-fade-in flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">Ticket Management</h2>
          <p className="mt-1 text-sm text-gray-400">
            Support tickets auto-generated from incidents or created manually.
          </p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} className="btn-primary">
          <Plus className="h-4 w-4" />
          New Ticket
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
        {[
          { label: "Total", value: stats.total, color: "text-sky-400" },
          { label: "Open", value: stats.open, color: "text-red-400" },
          { label: "In Progress", value: stats.in_progress, color: "text-amber-400" },
          { label: "Resolved", value: stats.resolved, color: "text-emerald-400" },
          { label: "Closed", value: stats.closed, color: "text-gray-400" },
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

      {showCreate && (
        <form onSubmit={handleCreate} className="card animate-fade-in space-y-4">
          <h3 className="text-base font-semibold text-gray-100">Create Ticket</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-400">Issue</label>
              <input
                required
                value={form.issue}
                onChange={(e) => setForm({ ...form, issue: e.target.value })}
                className="input-field"
                placeholder="Brief issue description"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-400">Priority</label>
              <select
                value={form.priority}
                onChange={(e) =>
                  setForm({ ...form, priority: e.target.value as TicketPriority })
                }
                className="input-field"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">Root Cause</label>
            <textarea
              required
              value={form.root_cause}
              onChange={(e) => setForm({ ...form, root_cause: e.target.value })}
              className="input-field min-h-[80px]"
              placeholder="Known or suspected root cause"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Assigned To (optional)
            </label>
            <input
              value={form.assigned_to}
              onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}
              className="input-field"
              placeholder="analyst username"
            />
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={creating} className="btn-primary">
              {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create"}
            </button>
            <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="card animate-fade-in">
        <div className="mb-4 flex items-center gap-2">
          <Ticket className="h-4 w-4 text-sky-400" />
          <h3 className="text-base font-semibold text-gray-100">Support Tickets</h3>
          <span className="ml-auto text-xs text-gray-500">{tickets.length} total</span>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
          </div>
        ) : tickets.length === 0 ? (
          <div className="py-12 text-center">
            <Ticket className="mx-auto h-10 w-10 text-gray-600" />
            <p className="mt-3 text-sm text-gray-500">
              No tickets yet. Parse logs to auto-generate tickets from incidents.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {tickets.map((ticket) => {
              const isExpanded = expandedId === ticket.ticket_id;
              return (
                <div
                  key={ticket.ticket_id}
                  className="rounded-lg border border-surface-border bg-surface transition-colors hover:border-sky-500/30"
                >
                  <button
                    onClick={() =>
                      setExpandedId(isExpanded ? null : ticket.ticket_id)
                    }
                    className="flex w-full items-center gap-3 p-4 text-left"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-500/10">
                      <Ticket className="h-4 w-4 text-amber-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-sm font-semibold text-sky-400">
                          {ticket.ticket_id}
                        </span>
                        <span
                          className={`rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase ${PRIORITY_STYLES[ticket.priority]}`}
                        >
                          {ticket.priority}
                        </span>
                        <span
                          className={`rounded px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[ticket.status]}`}
                        >
                          {STATUS_LABELS[ticket.status]}
                        </span>
                        {ticket.incident_ref && (
                          <span className="rounded bg-surface-hover px-2 py-0.5 text-xs text-gray-400">
                            {ticket.incident_ref}
                          </span>
                        )}
                      </div>
                      <p className="mt-1 truncate text-sm text-gray-400">{ticket.issue}</p>
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
                          <p className="mt-1 text-sm text-gray-300">{ticket.root_cause}</p>
                        </div>
                        <div>
                          <p className="text-xs font-medium uppercase text-gray-500">Assigned To</p>
                          <p className="mt-1 flex items-center gap-1.5 text-sm text-gray-300">
                            <User className="h-3.5 w-3.5 text-gray-500" />
                            {ticket.assigned_to || "Unassigned"}
                          </p>
                        </div>
                      </div>
                      <p className="mt-3 text-xs text-gray-500">
                        Created {new Date(ticket.created_at).toLocaleString()}
                      </p>
                      {ticket.status !== "closed" && (
                        <div className="mt-4 flex flex-wrap gap-2">
                          {ticket.status === "open" && (
                            <button
                              onClick={() => handleStatusUpdate(ticket.ticket_id, "in_progress")}
                              disabled={updatingId === ticket.ticket_id}
                              className="btn-secondary text-xs"
                            >
                              <Clock className="h-3.5 w-3.5" />
                              Start Progress
                            </button>
                          )}
                          {(ticket.status === "open" || ticket.status === "in_progress") && (
                            <button
                              onClick={() => handleStatusUpdate(ticket.ticket_id, "resolved")}
                              disabled={updatingId === ticket.ticket_id}
                              className="btn-primary text-xs"
                            >
                              <CheckCircle className="h-3.5 w-3.5" />
                              Resolve
                            </button>
                          )}
                          {ticket.status === "resolved" && (
                            <button
                              onClick={() => handleStatusUpdate(ticket.ticket_id, "closed")}
                              disabled={updatingId === ticket.ticket_id}
                              className="btn-secondary text-xs"
                            >
                              <XCircle className="h-3.5 w-3.5" />
                              Close
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(ticket.ticket_id)}
                            disabled={updatingId === ticket.ticket_id}
                            className="btn-secondary text-xs text-red-400 hover:border-red-500/40"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                            Delete
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
