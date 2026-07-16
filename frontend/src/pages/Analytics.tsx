import React, { useEffect, useState } from "react";
import { api } from "../lib/api";

export const Analytics: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.get("/analytics/history").then((res) => setHistory(res.data));
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">Analytics Insights Logs</h1>
        <p className="text-zinc-500 text-sm mt-1">Platform aggregated KPI values and statistical metrics</p>
      </div>

      <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-semibold">
              <th className="px-6 py-4">Execution ID</th>
              <th className="px-6 py-4">Total KPIs</th>
              <th className="px-6 py-4">Anomalies Detected</th>
              <th className="px-6 py-4">Created At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {history.map((row) => (
              <tr key={row.id} className="hover:bg-zinc-800/30 transition-all">
                <td className="px-6 py-4 font-mono text-zinc-400 text-xs">{row.id}</td>
                <td className="px-6 py-4">{row.kpis_json?.length || 0}</td>
                <td className="px-6 py-4">{row.anomalies_json?.length || 0}</td>
                <td className="px-6 py-4 text-zinc-500">{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center py-8 text-zinc-500">No analytics history registered yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
