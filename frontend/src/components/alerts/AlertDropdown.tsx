import { Bell, CheckCheck } from "lucide-react";
import { useState } from "react";
import { useAlerts } from "../../context/AlertContext";

const severityDot: Record<string, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-amber-500",
  low: "bg-sky-500",
  info: "bg-gray-500",
};

export default function AlertDropdown() {
  const { alerts, unreadCount, markAllRead, markRead, connected } = useAlerts();
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative rounded-lg p-2 text-gray-400 transition-colors hover:bg-surface-hover hover:text-gray-200"
        title={connected ? "Alerts connected" : "Alerts reconnecting..."}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
        <span
          className={`absolute bottom-1 right-1 h-1.5 w-1.5 rounded-full ${
            connected ? "bg-emerald-500" : "bg-amber-500"
          }`}
        />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-50 mt-2 w-80 rounded-lg border border-surface-border bg-surface-card shadow-xl">
            <div className="flex items-center justify-between border-b border-surface-border px-4 py-3">
              <h3 className="text-sm font-semibold text-gray-100">Alerts</h3>
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllRead()}
                  className="flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300"
                >
                  <CheckCheck className="h-3.5 w-3.5" />
                  Mark all read
                </button>
              )}
            </div>
            <div className="max-h-80 overflow-y-auto">
              {alerts.length === 0 ? (
                <p className="px-4 py-6 text-center text-xs text-gray-500">No alerts yet</p>
              ) : (
                alerts.slice(0, 10).map((alert) => (
                  <button
                    key={alert.alert_id}
                    onClick={() => {
                      if (!alert.is_read) markRead(alert.alert_id);
                    }}
                    className={`flex w-full items-start gap-3 border-b border-surface-border px-4 py-3 text-left transition-colors hover:bg-surface-hover ${
                      !alert.is_read ? "bg-sky-500/5" : ""
                    }`}
                  >
                    <span
                      className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${severityDot[alert.severity]}`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-medium text-gray-200">{alert.title}</p>
                      <p className="mt-0.5 truncate text-[11px] text-gray-500">{alert.message}</p>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
