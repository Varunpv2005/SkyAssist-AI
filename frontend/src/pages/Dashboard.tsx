import { useEffect, useState } from "react";
import { recentActivity, systemServices } from "../data/dashboardStats";
import StatCard from "../components/dashboard/StatCard";
import RecentActivity from "../components/dashboard/RecentActivity";
import SystemStatus from "../components/dashboard/SystemStatus";
import { useAuth } from "../context/AuthContext";
import { useAlerts } from "../context/AlertContext";
import { alertsApi, incidentsApi, ticketsApi } from "../services/api";
import type { DashboardStat } from "../types";

export default function Dashboard() {
  const { user } = useAuth();
  const { activity, connected } = useAlerts();
  const liveActivity = activity.length > 0 ? activity : recentActivity;
  const [stats, setStats] = useState<DashboardStat[]>([]);

  useEffect(() => {
    let cancelled = false;

    async function loadStats() {
      try {
        const [incidents, tickets, alerts] = await Promise.all([
          incidentsApi.stats(),
          ticketsApi.stats(),
          alertsApi.stats(),
        ]);
        if (cancelled) return;

        setStats([
          {
            label: "Total Incidents",
            value: incidents.total,
            change: 0,
            trend: "neutral",
            icon: "alert-triangle",
            color: "sky",
          },
          {
            label: "Critical Incidents",
            value: incidents.critical,
            change: 0,
            trend: "neutral",
            icon: "shield-alert",
            color: "red",
          },
          {
            label: "Resolved Incidents",
            value: incidents.resolved,
            change: 0,
            trend: "neutral",
            icon: "check-circle",
            color: "green",
          },
          {
            label: "Open Tickets",
            value: tickets.open,
            change: 0,
            trend: "neutral",
            icon: "ticket",
            color: "amber",
          },
          {
            label: "Active Alerts",
            value: alerts.unread,
            change: 0,
            trend: "neutral",
            icon: "bell",
            color: "purple",
          },
        ]);
      } catch {
        if (!cancelled) setStats([]);
      }
    }

    loadStats();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-gray-100">
          Security Operations Center
        </h2>
        <p className="mt-1 text-sm text-gray-400">
          Welcome back,{" "}
          <span className="font-medium text-sky-400">{user?.username}</span>.
          Here&apos;s your incident overview.
          {connected && (
            <span className="ml-2 inline-flex items-center gap-1 text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Live
            </span>
          )}
        </p>
      </div>

      {stats.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {stats.map((stat, index) => (
            <StatCard key={stat.label} stat={stat} index={index} />
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentActivity items={liveActivity} isLive={activity.length > 0} />
        </div>
        <div>
          <SystemStatus services={systemServices} />
        </div>
      </div>
    </div>
  );
}
