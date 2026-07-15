import { useCallback, useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { BarChart3, Loader2 } from "lucide-react";
import { analyticsApi } from "../services/api";
import type { AnalyticsData, AnalyticsPeriod } from "../types";

const PERIODS: { value: AnalyticsPeriod; label: string }[] = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
];

const CHART_COLORS = ["#38bdf8", "#f87171", "#fbbf24", "#34d399", "#a78bfa", "#fb923c", "#94a3b8"];

const tooltipStyle = {
  contentStyle: {
    backgroundColor: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "8px",
    fontSize: "12px",
  },
  labelStyle: { color: "#e2e8f0" },
};

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="card animate-fade-in">
      <h3 className="mb-4 text-sm font-semibold text-gray-100">{title}</h3>
      <div className="h-64">{children}</div>
    </div>
  );
}

export default function Analytics() {
  const [period, setPeriod] = useState<AnalyticsPeriod>("daily");
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await analyticsApi.get(period);
      setData(result);
    } catch {
      setError("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="space-y-6">
      <div className="animate-fade-in flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">Analytics Dashboard</h2>
          <p className="mt-1 text-sm text-gray-400">
            Incident trends, severity breakdown, and operational metrics.
          </p>
        </div>
        <div className="flex rounded-lg border border-surface-border bg-surface p-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
                period === p.value
                  ? "bg-sky-500/20 text-sky-400"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {data && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { label: "Incidents", value: data.summary.incidents ?? 0, color: "text-sky-400" },
            { label: "Tickets", value: data.summary.tickets ?? 0, color: "text-amber-400" },
            { label: "Alerts", value: data.summary.alerts ?? 0, color: "text-purple-400" },
            { label: "Critical", value: data.summary.critical ?? 0, color: "text-red-400" },
          ].map((s) => (
            <div key={s.label} className="card-hover">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-sm text-gray-400">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChartCard title="Incident Trends">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.incident_trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} allowDecimals={false} />
                <Tooltip {...tooltipStyle} />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  dot={{ fill: "#38bdf8", r: 3 }}
                  name="Incidents"
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Severity Distribution">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.severity_distribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ name, percent }) =>
                    `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                  }
                  labelLine={{ stroke: "#64748b" }}
                >
                  {data.severity_distribution.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip {...tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Top Error Categories">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_error_categories} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 10 }} allowDecimals={false} />
                <YAxis
                  type="category"
                  dataKey="category"
                  tick={{ fill: "#94a3b8", fontSize: 10 }}
                  width={100}
                />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="count" fill="#f87171" name="Count" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Resolved vs Unresolved">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.resolved_vs_unresolved}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} allowDecimals={false} />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="value" name="Incidents" radius={[4, 4, 0, 0]}>
                  {data.resolved_vs_unresolved.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={entry.name === "Resolved" ? "#34d399" : "#f87171"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Alert Frequency">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.alert_frequency}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} allowDecimals={false} />
                <Tooltip {...tooltipStyle} />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#a78bfa"
                  strokeWidth={2}
                  dot={{ fill: "#a78bfa", r: 3 }}
                  name="Alerts"
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Ticket Status">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.ticket_status}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ name, value }) => `${name}: ${value}`}
                  labelLine={{ stroke: "#64748b" }}
                >
                  {data.ticket_status.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip {...tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: "11px", color: "#94a3b8" }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      ) : (
        <div className="card py-16 text-center">
          <BarChart3 className="mx-auto h-10 w-10 text-gray-600" />
          <p className="mt-3 text-sm text-gray-500">
            No analytics data yet. Upload and parse logs to populate charts.
          </p>
        </div>
      )}
    </div>
  );
}
