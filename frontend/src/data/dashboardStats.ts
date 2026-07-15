import type { DashboardStat, ActivityItem } from "../types";

export const dashboardStats: DashboardStat[] = [
  {
    label: "Total Incidents",
    value: 147,
    change: 12,
    trend: "up",
    icon: "alert-triangle",
    color: "sky",
  },
  {
    label: "Critical Incidents",
    value: 8,
    change: -3,
    trend: "down",
    icon: "shield-alert",
    color: "red",
  },
  {
    label: "Resolved Incidents",
    value: 112,
    change: 18,
    trend: "up",
    icon: "check-circle",
    color: "green",
  },
  {
    label: "Open Tickets",
    value: 23,
    change: 5,
    trend: "up",
    icon: "ticket",
    color: "amber",
  },
  {
    label: "Active Alerts",
    value: 15,
    change: -2,
    trend: "down",
    icon: "bell",
    color: "purple",
  },
];

export const recentActivity: ActivityItem[] = [
  {
    id: "1",
    type: "incident",
    title: "AUTH_FAILURE detected",
    description: "Multiple failed login attempts from 192.168.1.45",
    severity: "critical",
    timestamp: "2 min ago",
  },
  {
    id: "2",
    type: "ticket",
    title: "INC-1042 created",
    description: "API timeout on /api/v1/proxy endpoint",
    severity: "high",
    timestamp: "8 min ago",
  },
  {
    id: "3",
    type: "alert",
    title: "SSL certificate expiring",
    description: "gateway.skyhigh.local cert expires in 7 days",
    severity: "medium",
    timestamp: "15 min ago",
  },
  {
    id: "4",
    type: "log",
    title: "Log file uploaded",
    description: "proxy_access_2026-06-15.log parsed successfully",
    severity: "info",
    timestamp: "22 min ago",
  },
  {
    id: "5",
    type: "incident",
    title: "DATABASE_CONNECTION_ERROR",
    description: "Connection pool exhausted on primary DB",
    severity: "critical",
    timestamp: "35 min ago",
  },
  {
    id: "6",
    type: "ticket",
    title: "INC-1041 resolved",
    description: "DNS resolution failure — root cause: stale cache",
    severity: "low",
    timestamp: "1 hr ago",
  },
];

export const systemServices = [
  { name: "API Gateway", status: "operational" as const, uptime: "99.98%" },
  { name: "Auth Service", status: "operational" as const, uptime: "99.95%" },
  { name: "Log Parser", status: "degraded" as const, uptime: "98.12%" },
  { name: "Incident Engine", status: "operational" as const, uptime: "99.87%" },
  { name: "AI Assistant", status: "operational" as const, uptime: "99.50%" },
];
