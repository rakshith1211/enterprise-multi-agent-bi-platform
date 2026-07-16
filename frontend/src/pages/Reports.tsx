import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { FileText } from "lucide-react";

export const Reports: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.get("/reports/history").then((res) => setHistory(res.data));
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">Executive Reports</h1>
        <p className="text-zinc-500 text-sm mt-1">Download compiled corporate reports and executive memos</p>
      </div>

      <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-semibold">
              <th className="px-6 py-4">Title</th>
              <th className="px-6 py-4">Page Length</th>
              <th className="px-6 py-4">Downloads</th>
              <th className="px-6 py-4">Created At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {history.map((row) => (
              <tr key={row.id} className="hover:bg-zinc-800/30 transition-all">
                <td className="px-6 py-4 font-semibold text-zinc-300">{row.report_metadata?.title || "Untitled Memo"}</td>
                <td className="px-6 py-4 text-zinc-400">{row.report_metadata?.pages_count || 1} pages</td>
                <td className="px-6 py-4 flex gap-3">
                  <a
                    href={`http://localhost:8000/api/v1/reports/download/${row.id}?format=pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium"
                  >
                    <FileText size={14} /> PDF
                  </a>
                  <a
                    href={`http://localhost:8000/api/v1/reports/download/${row.id}?format=docx`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium"
                  >
                    <FileText size={14} /> Word
                  </a>
                  <a
                    href={`http://localhost:8000/api/v1/reports/download/${row.id}?format=pptx`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-purple-400 hover:text-purple-300 font-medium"
                  >
                    <FileText size={14} /> PPTX
                  </a>
                </td>
                <td className="px-6 py-4 text-zinc-500">{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center py-8 text-zinc-500">No reports generated yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
