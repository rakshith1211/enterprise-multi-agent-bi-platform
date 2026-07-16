import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import { Sidebar } from "./components/Sidebar";

// Pages
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Chat } from "./pages/Chat";
import { Analytics } from "./pages/Analytics";
import { Visualizations } from "./pages/Visualizations";
import { Forecasts } from "./pages/Forecasts";
import { Recommendations } from "./pages/Recommendations";
import { Reports } from "./pages/Reports";
import { Documents } from "./pages/Documents";
import { Connections } from "./pages/Connections";
import { WorkflowMonitor } from "./pages/WorkflowMonitor";
import { Settings } from "./pages/Settings";

// Protect Routes wrapper
const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-zinc-950">
      <Sidebar />
      <main className="flex-1 overflow-x-hidden overflow-y-auto bg-zinc-950">
        {children}
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Guarded Application Views */}
        <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
        <Route path="/chat" element={<ProtectedLayout><Chat /></ProtectedLayout>} />
        <Route path="/analytics" element={<ProtectedLayout><Analytics /></ProtectedLayout>} />
        <Route path="/visualizations" element={<ProtectedLayout><Visualizations /></ProtectedLayout>} />
        <Route path="/forecasts" element={<ProtectedLayout><Forecasts /></ProtectedLayout>} />
        <Route path="/recommendations" element={<ProtectedLayout><Recommendations /></ProtectedLayout>} />
        <Route path="/reports" element={<ProtectedLayout><Reports /></ProtectedLayout>} />
        <Route path="/documents" element={<ProtectedLayout><Documents /></ProtectedLayout>} />
        <Route path="/connections" element={<ProtectedLayout><Connections /></ProtectedLayout>} />
        <Route path="/monitor" element={<ProtectedLayout><WorkflowMonitor /></ProtectedLayout>} />
        <Route path="/settings" element={<ProtectedLayout><Settings /></ProtectedLayout>} />

        {/* Defaults */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
