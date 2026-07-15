import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Sun,
  Moon,
  LogOut,
  User,
  Menu,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import AlertDropdown from "../alerts/AlertDropdown";

interface NavbarProps {
  onMenuClick: () => void;
  sidebarCollapsed: boolean;
}

export default function Navbar({ onMenuClick, sidebarCollapsed }: NavbarProps) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showProfile, setShowProfile] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header
      className={`fixed left-0 right-0 top-0 z-30 flex h-16 items-center justify-between border-b border-surface-border bg-surface-card/80 px-4 backdrop-blur-md transition-all duration-300 lg:left-auto ${
        sidebarCollapsed ? "lg:left-[72px]" : "lg:left-64"
      }`}
    >
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-surface-hover hover:text-gray-200 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && searchQuery.trim()) {
                navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
              }
            }}
            placeholder="Search incidents, tickets, logs..."
            aria-label="Global search"
            className="input-field w-72 pl-10 lg:w-96"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-surface-hover hover:text-gray-200"
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        <AlertDropdown />

        <div className="relative">
          <button
            onClick={() => setShowProfile(!showProfile)}
            className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-surface-hover"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sky-500/20 text-sm font-semibold text-sky-400">
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <div className="hidden text-left md:block">
              <p className="text-sm font-medium text-gray-200">
                {user?.username || "User"}
              </p>
              <p className="text-[11px] capitalize text-gray-500">{user?.role}</p>
            </div>
          </button>

          {showProfile && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowProfile(false)}
              />
              <div className="absolute right-0 z-50 mt-2 w-48 rounded-lg border border-surface-border bg-surface-card py-1 shadow-xl">
                <div className="border-b border-surface-border px-4 py-2">
                  <p className="text-sm font-medium text-gray-200">
                    {user?.username}
                  </p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <button className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-400 hover:bg-surface-hover hover:text-gray-200">
                  <User className="h-4 w-4" />
                  Profile
                </button>
                <button
                  onClick={logout}
                  className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-red-500/10"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
