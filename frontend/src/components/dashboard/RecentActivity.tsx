import { AlertTriangle, Bell, FileText, Ticket } from "lucide-react";
import type { ActivityItem } from "../../types";

const typeIcons = {
  incident: AlertTriangle,
  ticket: Ticket,
  alert: Bell,
  log: FileText,
};

const severityColors = {
  critical: "bg-red-500/15 text-red-400 border-red-500/30",
  high: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  low: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  info: "bg-gray-500/15 text-gray-400 border-gray-500/30",
};

interface RecentActivityProps {
  items: ActivityItem[];
  isLive?: boolean;
}

export default function RecentActivity({ items, isLive = false }: RecentActivityProps) {
  return (
    <div className="card animate-fade-in" style={{ animationDelay: "400ms" }}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-100">Recent Activity</h3>
        {isLive && (
          <span className="rounded-full bg-sky-500/10 px-2.5 py-0.5 text-xs font-medium text-sky-400">
            Live
          </span>
        )}
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const Icon = typeIcons[item.type];
          return (
            <div
              key={item.id}
              className="group flex items-start gap-3 rounded-lg border border-transparent p-3 transition-all hover:border-surface-border hover:bg-surface-hover"
            >
              <div className="mt-0.5 rounded-lg bg-surface-hover p-2 transition-colors group-hover:bg-surface">
                <Icon className="h-4 w-4 text-gray-400" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate text-sm font-medium text-gray-200">
                    {item.title}
                  </p>
                  <span
                    className={`shrink-0 rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase ${severityColors[item.severity]}`}
                  >
                    {item.severity}
                  </span>
                </div>
                <p className="mt-0.5 truncate text-xs text-gray-500">
                  {item.description}
                </p>
              </div>
              <span className="shrink-0 text-xs text-gray-500">{item.timestamp}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
