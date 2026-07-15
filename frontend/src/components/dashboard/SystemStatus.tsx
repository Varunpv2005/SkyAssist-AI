import { Activity, CheckCircle, AlertCircle } from "lucide-react";

interface Service {
  name: string;
  status: "operational" | "degraded" | "down";
  uptime: string;
}

interface SystemStatusProps {
  services: Service[];
}

const statusConfig = {
  operational: {
    icon: CheckCircle,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    label: "Operational",
  },
  degraded: {
    icon: AlertCircle,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    label: "Degraded",
  },
  down: {
    icon: AlertCircle,
    color: "text-red-400",
    bg: "bg-red-500/10",
    label: "Down",
  },
};

export default function SystemStatus({ services }: SystemStatusProps) {
  const operational = services.filter((s) => s.status === "operational").length;

  return (
    <div className="card animate-fade-in" style={{ animationDelay: "500ms" }}>
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-sky-400" />
          <h3 className="text-base font-semibold text-gray-100">System Status</h3>
        </div>
        <span className="text-xs text-gray-400">
          {operational}/{services.length} healthy
        </span>
      </div>

      <div className="space-y-2">
        {services.map((service) => {
          const config = statusConfig[service.status];
          const StatusIcon = config.icon;

          return (
            <div
              key={service.name}
              className="flex items-center justify-between rounded-lg bg-surface-hover/50 px-3 py-2.5"
            >
              <div className="flex items-center gap-2.5">
                <div className={`rounded-full p-1 ${config.bg}`}>
                  <StatusIcon className={`h-3.5 w-3.5 ${config.color}`} />
                </div>
                <span className="text-sm text-gray-300">{service.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">{service.uptime}</span>
                <span className={`text-xs font-medium ${config.color}`}>
                  {config.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
