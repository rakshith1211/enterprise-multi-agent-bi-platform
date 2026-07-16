import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Database, FolderOpen, BarChart3, Activity } from "lucide-react";

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    connections: 0,
    catalogTerms: 0,
    workflowsRun: 0,
    ragDocs: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [conn, cat, wf, rag] = await Promise.all([
          api.get("/connections"),
          api.get("/catalog/terms"),
          api.get("/workflow/history"),
          api.get("/rag/history"),
        ]);
        setStats({
          connections: conn.data.length,
          catalogTerms: cat.data.length,
          workflowsRun: wf.data.length,
          ragDocs: rag.data.length,
        });
      } catch (err) {
        console.error("Dashboard statistics loading failed", err);
      }
    };
    fetchStats();
  }, []);

  const cards = [
    { title: "Active DB Connections", val: stats.connections, icon: <Database className="text-cyan-400" size={24} />, desc: "Configured database connectors" },
    { title: "Semantic Glossary Terms", val: stats.catalogTerms, icon: <BarChart3 className="text-blue-400" size={24} />, desc: "Indexed database columns definitions" },
    { title: "RAG Documentation Chunks", val: stats.ragDocs, icon: <FolderOpen className="text-emerald-400" size={24} />, desc: "Ingested PDF, docx, CSV vectors" },
    { title: "Agent Workflows Executed", val: stats.workflowsRun, icon: <Activity className="text-purple-400" size={24} />, desc: "LangGraph orchestration runs" },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-extrabold text-zinc-100">BI Analytics Overview</h1>
        <p className="text-zinc-500 text-sm mt-1">Platform metrics health dashboard</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((c, idx) => (
          <div key={idx} className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-xl flex items-center justify-between shadow-lg">
            <div className="space-y-2">
              <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">{c.title}</span>
              <div className="text-3xl font-extrabold text-zinc-100">{c.val}</div>
              <p className="text-xs text-zinc-500">{c.desc}</p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center">
              {c.icon}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
