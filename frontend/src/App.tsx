import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { ProtectedRoute, PublicRoute } from "./components/auth/ProtectedRoute";
import DashboardLayout from "./components/layout/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Logs from "./pages/Logs";
import Incidents from "./pages/Incidents";
import Analysis from "./pages/Analysis";
import AIAssistant from "./pages/AIAssistant";
import Tickets from "./pages/Tickets";
import Analytics from "./pages/Analytics";
import SearchPage from "./pages/Search";
import Knowledge from "./pages/Knowledge";
import Login from "./pages/Login";
import Register from "./pages/Register";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            <Route element={<PublicRoute />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>

            <Route element={<ProtectedRoute />}>
              <Route element={<DashboardLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/logs" element={<Logs />} />
                <Route path="/incidents" element={<Incidents />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/ai-assistant" element={<AIAssistant />} />
                <Route path="/tickets" element={<Tickets />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/knowledge" element={<Knowledge />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
