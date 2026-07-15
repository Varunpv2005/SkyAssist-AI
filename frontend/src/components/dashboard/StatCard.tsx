import {
  AlertTriangle,
  Bell,
  CheckCircle,
  ShieldAlert,
  Ticket,
  TrendingDown,
  TrendingUp,
  Minus,
} from "lucide-react";
import type { DashboardStat } from "../../types";

const iconMap = {
  "alert-triangle": AlertTriangle,
  "shield-alert": ShieldAlert,
  "check-circle": CheckCircle,
  ticket: Ticket,
  bell: Bell,
};

const colorMap = {
  sky: {
    bg: "bg-sky-500/10",
    text: "text-sky-400",
    border: "border-sky-500/20",
    glow: "hover:shadow-sky-500/10",
  },
  red: {
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/20",
    glow: "hover:shadow-red-500/10",
  },
  green: {
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/20",
    glow: "hover:shadow-emerald-500/10",
  },
  amber: {
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/20",
    glow: "hover:shadow-amber-500/10",
  },
  purple: {
    bg: "bg-purple-500/10",
    text: "text-purple-400",
    border: "border-purple-500/20",
    glow: "hover:shadow-purple-500/10",
  },
};

interface StatCardProps {
  stat: DashboardStat;
  index: number;
}

export default function StatCard({ stat, index }: StatCardProps) {
  const Icon = iconMap[stat.icon as keyof typeof iconMap] || AlertTriangle;
  const colors = colorMap[stat.color];

  const TrendIcon =
    stat.trend === "up"
      ? TrendingUp
      : stat.trend === "down"
        ? TrendingDown
        : Minus;

  const trendColor =
    stat.trend === "up"
      ? stat.label.includes("Critical") || stat.label.includes("Open")
        ? "text-red-400"
        : "text-emerald-400"
      : stat.trend === "down"
        ? stat.label.includes("Critical") || stat.label.includes("Active")
          ? "text-emerald-400"
          : "text-red-400"
        : "text-gray-400";

  return (
    <div
      className={`card-hover animate-fade-in border ${colors.border} ${colors.glow}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className="flex items-start justify-between">
        <div className={`rounded-lg p-2.5 ${colors.bg}`}>
          <Icon className={`h-5 w-5 ${colors.text}`} />
        </div>
        <div className={`flex items-center gap-1 text-xs font-medium ${trendColor}`}>
          <TrendIcon className="h-3.5 w-3.5" />
          <span>{Math.abs(stat.change)}%</span>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-3xl font-bold tracking-tight text-gray-100">
          {stat.value.toLocaleString()}
        </p>
        <p className="mt-1 text-sm text-gray-400">{stat.label}</p>
      </div>
    </div>
  );
}
