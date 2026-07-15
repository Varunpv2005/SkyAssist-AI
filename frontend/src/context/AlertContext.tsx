import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { alertsApi } from "../services/api";
import type { ActivityItem, Alert, AlertSeverity } from "../types";
import { useAuth } from "./AuthContext";

interface Toast {
  id: string;
  title: string;
  message: string;
  severity: AlertSeverity;
}

interface AlertContextValue {
  alerts: Alert[];
  activity: ActivityItem[];
  unreadCount: number;
  toasts: Toast[];
  connected: boolean;
  dismissToast: (id: string) => void;
  markAllRead: () => Promise<void>;
  markRead: (alertId: string) => Promise<void>;
}

const AlertContext = createContext<AlertContextValue | null>(null);

function alertToActivity(alert: Alert): ActivityItem {
  const typeMap = {
    incident: "incident" as const,
    ticket: "ticket" as const,
    system: "alert" as const,
  };
  return {
    id: alert.alert_id,
    type: typeMap[alert.alert_type] || "alert",
    title: alert.title,
    description: alert.message,
    severity: alert.severity === "info" ? "info" : alert.severity,
    timestamp: formatRelativeTime(alert.created_at),
  };
}

function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr ago`;
  return new Date(iso).toLocaleDateString();
}

function getWsUrl(token: string): string {
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) {
    const parsed = new URL(apiUrl, window.location.origin);
    const protocol = parsed.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${parsed.host}/ws?token=${encodeURIComponent(token)}`;
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws?token=${encodeURIComponent(token)}`;
}

export function AlertProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const handleIncomingAlert = useCallback((alert: Alert) => {
    setAlerts((prev) => [alert, ...prev].slice(0, 50));
    setActivity((prev) => [alertToActivity(alert), ...prev].slice(0, 20));
    if (!alert.is_read) {
      setUnreadCount((c) => c + 1);
    }
    const toast: Toast = {
      id: alert.alert_id,
      title: alert.title,
      message: alert.message,
      severity: alert.severity,
    };
    setToasts((prev) => [...prev, toast].slice(-5));
    setTimeout(() => dismissToast(alert.alert_id), 5000);
  }, [dismissToast]);

  const fetchAlerts = useCallback(async () => {
    try {
      const data = await alertsApi.list();
      setAlerts(data.alerts);
      setUnreadCount(data.unread);
      setActivity(data.alerts.map(alertToActivity));
    } catch {
      // silent — WS may still deliver live alerts
    }
  }, []);

  const markRead = useCallback(async (alertId: string) => {
    try {
      await alertsApi.markRead(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.alert_id === alertId ? { ...a, is_read: true } : a)),
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {
      // keep UI in sync with server on next fetch
    }
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await alertsApi.markAllRead();
      setAlerts((prev) => prev.map((a) => ({ ...a, is_read: true })));
      setUnreadCount(0);
    } catch {
      // keep UI in sync with server on next fetch
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      wsRef.current?.close();
      setConnected(false);
      return;
    }

    fetchAlerts();

    const token = localStorage.getItem("skyassist_token");
    if (!token) return;

    let mounted = true;
    reconnectAttempts.current = 0;

    const connect = () => {
      if (!mounted) return;
      if (reconnectAttempts.current >= 20) return;

      const ws = new WebSocket(getWsUrl(token));
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mounted) { ws.close(); return; }
        setConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        if (!mounted) return;
        try {
          const data = JSON.parse(event.data);
          if (data.event === "alert" && data.alert) {
            handleIncomingAlert(data.alert as Alert);
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        if (!mounted) return;
        setConnected(false);
        reconnectAttempts.current += 1;
        const delay = Math.min(2000 * reconnectAttempts.current, 30000);
        reconnectRef.current = setTimeout(connect, delay);
      };

      ws.onerror = () => ws.close();
    };

    connect();

    return () => {
      mounted = false;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [isAuthenticated, fetchAlerts, handleIncomingAlert]);

  return (
    <AlertContext.Provider
      value={{
        alerts,
        activity,
        unreadCount,
        toasts,
        connected,
        dismissToast,
        markAllRead,
        markRead,
      }}
    >
      {children}
    </AlertContext.Provider>
  );
}

export function useAlerts() {
  const ctx = useContext(AlertContext);
  if (!ctx) throw new Error("useAlerts must be used within AlertProvider");
  return ctx;
}
