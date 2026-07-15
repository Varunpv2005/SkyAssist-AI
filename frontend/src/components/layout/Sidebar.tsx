import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  AlertTriangle,
  Search,
  Ticket,
  Bot,
  BarChart3,
  BookOpen,
  Shield,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/search", icon: Search, label: "Search" },
  { to: "/logs", icon: FileText, label: "Logs" },
  { to: "/incidents", icon: AlertTriangle, label: "Incidents" },
  { to: "/analysis", icon: AlertTriangle, label: "Root Cause" },
  { to: "/tickets", icon: Ticket, label: "Tickets" },
  { to: "/knowledge", icon: BookOpen, label: "Knowledge" },
  { to: "/ai-assistant", icon: Bot, label: "AI Assistant" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={`fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-surface-border bg-surface-card transition-all duration-300 ${
        collapsed ? "w-[72px]" : "w-64"
      }`}
    >
      <div className="flex h-16 items-center gap-3 border-b border-surface-border px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sky-500/15">
          <Shield className="h-5 w-5 text-sky-400" />
        </div>
        {!collapsed && (
          <div className="animate-slide-in overflow-hidden">
            <h1 className="text-sm font-bold tracking-wide text-gray-100">
              SKYASSIST
            </h1>
            <p className="text-[10px] font-medium uppercase tracking-widest text-sky-400">
              AI Security
            </p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `${isActive ? "nav-link-active" : "nav-link"} ${collapsed ? "justify-center px-2" : ""}`
            }
            title={collapsed ? item.label : undefined}
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-surface-border p-3">
        <button
          onClick={onToggle}
          className={`nav-link mt-1 w-full ${collapsed ? "justify-center px-2" : ""}`}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <>
              <ChevronLeft className="h-5 w-5" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
