import { useCallback, useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Search, Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import { searchApi } from "../services/api";
import type { SearchHit, SearchScope } from "../types";

const SCOPES: { value: SearchScope; label: string }[] = [
  { value: "all", label: "All" },
  { value: "incidents", label: "Incidents" },
  { value: "logs", label: "Logs" },
  { value: "tickets", label: "Tickets" },
  { value: "ai", label: "AI History" },
  { value: "knowledge", label: "Knowledge" },
];

const TYPE_COLORS: Record<string, string> = {
  incident: "text-red-400",
  ticket: "text-amber-400",
  log: "text-sky-400",
  ai: "text-purple-400",
  knowledge: "text-emerald-400",
};

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get("q") || "");
  const [scope, setScope] = useState<SearchScope>((params.get("scope") as SearchScope) || "all");
  const [severity, setSeverity] = useState(params.get("severity") || "");
  const [status, setStatus] = useState(params.get("status") || "");
  const [page, setPage] = useState(1);
  const [results, setResults] = useState<SearchHit[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [loading, setLoading] = useState(false);

  const runSearch = useCallback(async () => {
    setLoading(true);
    try {
      const data = await searchApi.search({
        q: query || undefined,
        scope,
        severity: severity || undefined,
        status: status || undefined,
        page,
        page_size: 15,
      });
      setResults(data.results);
      setTotal(data.total);
      setPages(data.pages);
    } finally {
      setLoading(false);
    }
  }, [query, scope, severity, status, page]);

  useEffect(() => {
    runSearch();
  }, [runSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setParams({ q: query, scope, ...(severity && { severity }), ...(status && { status }) });
    runSearch();
  };

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-gray-100">Enterprise Search</h2>
        <p className="mt-1 text-sm text-gray-400">Search incidents, logs, tickets, AI history, and knowledge base.</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by ID, description, error message..."
            className="input-field w-full pl-10"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {SCOPES.map((s) => (
            <button
              key={s.value}
              type="button"
              onClick={() => { setScope(s.value); setPage(1); }}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                scope === s.value ? "bg-sky-500/20 text-sky-400" : "bg-surface-hover text-gray-400"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="input-field text-sm">
            <option value="">All severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="input-field text-sm">
            <option value="">All statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <button type="submit" className="btn-primary">Search</button>
        </div>
      </form>

      <div className="card">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-gray-400">{total} results</span>
          {pages > 1 && (
            <div className="flex items-center gap-2">
              <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn-secondary p-2">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-xs text-gray-500">{page} / {pages}</span>
              <button disabled={page >= pages} onClick={() => setPage(page + 1)} className="btn-secondary p-2">
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-sky-400" /></div>
        ) : results.length === 0 ? (
          <p className="py-12 text-center text-sm text-gray-500">No results found</p>
        ) : (
          <div className="space-y-2">
            {results.map((r) => (
              <Link
                key={`${r.type}-${r.id}`}
                to={r.link}
                className="flex items-start gap-3 rounded-lg border border-surface-border p-3 transition-colors hover:border-sky-500/30 hover:bg-surface-hover"
              >
                <span className={`mt-0.5 text-xs font-bold uppercase ${TYPE_COLORS[r.type] || "text-gray-400"}`}>
                  {r.type}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-gray-200">{r.title}</p>
                  {r.subtitle && <p className="mt-0.5 truncate text-sm text-gray-500">{r.subtitle}</p>}
                  <div className="mt-1 flex gap-2 text-xs text-gray-500">
                    {r.severity && <span>{r.severity}</span>}
                    {r.status && <span className="capitalize">{r.status.replace("_", " ")}</span>}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
