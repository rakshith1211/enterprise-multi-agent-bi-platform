import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  LayoutDashboard,
  MessageSquare,
  TrendingUp,
  BarChart3,
  Lightbulb,
  FileText,
  Database,
  Activity,
  LogOut,
  FolderOpen
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const links = [
    { to: "/dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} /> },
    { to: "/chat", label: "AI Chat", icon: <MessageSquare size={18} /> },
    { to: "/analytics", label: "Analytics", icon: <BarChart3 size={18} /> },
    { to: "/forecasts", label: "Forecasts", icon: <TrendingUp size={18} /> },
    { to: "/recommendations", label: "Recommendations", icon: <Lightbulb size={18} /> },
    { to: "/reports", label: "Reports", icon: <FileText size={18} /> },
    { to: "/documents", label: "RAG Documents", icon: <FolderOpen size={18} /> },
    { to: "/connections", label: "Connections", icon: <Database size={18} /> },
    { to: "/monitor", label: "Workflow Monitor", icon: <Activity size={18} /> },
  ];

  return (
    <aside className="w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col justify-between h-screen sticky top-0">
      <div className="flex flex-col">
        {/* Title Brand */}
        <div className="h-16 flex items-center px-6 border-b border-zinc-800">
          <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Antigravity BI
          </span>
        </div>

        {/* Links Navigation */}
        <nav className="p-4 space-y-1.5 flex-1 overflow-y-auto">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-4 py-2.5 rounded-lg text-sm transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-500 font-medium"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                }`
              }
            >
              {link.icon}
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer / Logout */}
      <div className="p-4 border-t border-zinc-800 flex flex-col gap-3">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 text-xs font-bold uppercase">
            {user?.username.slice(0, 2) || "US"}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium text-zinc-300 truncate">{user?.username || "User"}</span>
            <span className="text-xs text-zinc-500 capitalize">{user?.role || "Viewer"}</span>
          </div>
        </div>
        <button
          onClick={() => {
            logout();
            navigate("/login");
          }}
          className="flex items-center gap-3.5 px-4 py-2.5 rounded-lg text-sm text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-all w-full text-left"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </aside>
  );
};
