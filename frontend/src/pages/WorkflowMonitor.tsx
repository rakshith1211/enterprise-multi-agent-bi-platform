import React, { useEffect, useState } from "react";
import { api } from "../lib/api";

export const WorkflowMonitor: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.get("/workflow/history").then((res) => setHistory(res.data));
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">Workflow Monitor Logs</h1>
        <p className="text-zinc-500 text-sm mt-1">Multi-agent orchestrations trace logs and pipeline step runs</p>
      </div>

      <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-semibold">
              <th className="px-6 py-4">Workflow ID</th>
              <th className="px-6 py-4">Query</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Created At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {history.map((row) => (
              <tr key={row.id} className="hover:bg-zinc-800/30 transition-all">
                <td className="px-6 py-4 font-mono text-zinc-400 text-xs">{row.id}</td>
                <td className="px-6 py-4 font-medium text-zinc-300">{row.user_query}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${row.status === "success" ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
                    {row.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-zinc-500">{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center py-8 text-zinc-500">No workflow traces registered yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
