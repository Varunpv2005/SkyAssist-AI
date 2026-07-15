import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import ToastContainer from "../alerts/ToastContainer";
import { AlertProvider } from "../../context/AlertContext";

export default function DashboardLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <AlertProvider>
      <div className="min-h-screen bg-surface">
      <div
        className={`fixed inset-y-0 left-0 z-40 transition-transform duration-300 lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <Sidebar
          collapsed={sidebarCollapsed && !mobileOpen}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <Navbar
        onMenuClick={() => setMobileOpen(!mobileOpen)}
        sidebarCollapsed={sidebarCollapsed}
      />

      <main
        id="main-content"
        className={`min-h-screen pt-16 transition-all duration-300 pl-0 ${
          sidebarCollapsed ? "lg:pl-[72px]" : "lg:pl-64"
        }`}
      >
        <div className="p-4 md:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
      <ToastContainer />
    </div>
    </AlertProvider>
  );
}
