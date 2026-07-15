import { AlertTriangle, Bell, CheckCircle, X } from "lucide-react";
import { useAlerts } from "../../context/AlertContext";
import type { AlertSeverity } from "../../types";

const severityStyles: Record<AlertSeverity, string> = {
  critical: "border-red-500/40 bg-red-500/10",
  high: "border-orange-500/40 bg-orange-500/10",
  medium: "border-amber-500/40 bg-amber-500/10",
  low: "border-sky-500/40 bg-sky-500/10",
  info: "border-gray-500/40 bg-gray-500/10",
};

const severityIcons: Record<AlertSeverity, typeof AlertTriangle> = {
  critical: AlertTriangle,
  high: AlertTriangle,
  medium: Bell,
  low: CheckCircle,
  info: Bell,
};

export default function ToastContainer() {
  const { toasts, dismissToast } = useAlerts();

  if (toasts.length === 0) return null;

  return (
    <div className="pointer-events-none fixed right-4 top-20 z-50 flex w-full max-w-sm flex-col gap-2">
      {toasts.map((toast) => {
        const Icon = severityIcons[toast.severity];
        return (
          <div
            key={toast.id}
            className={`pointer-events-auto animate-slide-in rounded-lg border p-4 shadow-xl backdrop-blur-md ${severityStyles[toast.severity]}`}
          >
            <div className="flex items-start gap-3">
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-gray-300" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-gray-100">{toast.title}</p>
                <p className="mt-0.5 text-xs text-gray-400 line-clamp-2">{toast.message}</p>
              </div>
              <button
                onClick={() => dismissToast(toast.id)}
                className="shrink-0 rounded p-0.5 text-gray-500 hover:text-gray-300"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
