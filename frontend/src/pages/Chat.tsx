import React, { useState, useEffect } from "react";
import { api } from "../lib/api";
import { Send, Terminal, FileText, CheckCircle2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  text: string;
  sql?: string;
  trace?: string[];
  reportUrl?: string;
  plotlySpec?: any;
}

export const Chat: React.FC = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Welcome to Antigravity BI. How can I help you query and analyze your business datasets today?" },
  ]);
  const [connections, setConnections] = useState<any[]>([]);
  const [selectedConn, setSelectedConn] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/connections").then((res) => {
      setConnections(res.data);
      if (res.data.length > 0) setSelectedConn(res.data[0].id);
    });
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedConn) return;

    const userMsg = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);

    try {
      const response = await api.post("/workflow/run", {
        user_query: userMsg,
        connection_id: selectedConn,
        generate_report: true,
      });

      const data = response.data;
      
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.recommendations?.recommendations?.map((r: any) => `• ${r.opportunity || r.risk}: ${r.recommended_action}`).join("\n") || "Workflow completed successfully with metrics summary.",
          sql: data.sql,
          trace: data.trace,
          reportUrl: data.report?.id ? `http://localhost:8000/api/v1/reports/download/${data.report.id}?format=pdf` : undefined,
          plotlySpec: data.visualization?.plotly_spec,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Failed to execute multi-agent workflow orchestration." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      {/* Central Chat window */}
      <div className="flex-1 flex flex-col justify-between border-r border-zinc-800">
        {/* Chat header */}
        <div className="h-16 flex items-center justify-between px-8 border-b border-zinc-800">
          <div className="flex items-center gap-4">
            <h2 className="font-bold text-lg">AI Assistant</h2>
            <select
              value={selectedConn}
              onChange={(e) => setSelectedConn(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1 text-sm text-zinc-300"
            >
              <option value="">Select connection...</option>
              {connections.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Message logs */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-2xl rounded-2xl p-5 ${m.role === "user" ? "bg-cyan-600 text-white" : "bg-zinc-900 border border-zinc-800"} space-y-3.5`}>
                <p className="text-sm whitespace-pre-line leading-relaxed">{m.text}</p>
                
                {/* Embedded SQL */}
                {m.sql && (
                  <div className="mt-3 bg-zinc-950 p-3.5 rounded-lg border border-zinc-800 font-mono text-xs text-cyan-400 overflow-x-auto flex flex-col gap-2">
                    <div className="flex items-center gap-1.5 text-zinc-500 font-semibold uppercase tracking-wider">
                      <Terminal size={12} /> Generated SQL
                    </div>
                    {m.sql}
                  </div>
                )}

                {/* Plotly spec info */}
                {m.plotlySpec && (
                  <div className="mt-3 bg-zinc-950 p-4 rounded-lg border border-zinc-800 text-xs text-zinc-400">
                    <div className="flex items-center gap-1 text-emerald-400 font-bold mb-2">
                      <CheckCircle2 size={14} /> Spec recommendation: {m.plotlySpec.type || "Scatter plot"}
                    </div>
                    <span>Interactive Plotly specifications are compiled and cached in Redis.</span>
                  </div>
                )}

                {/* Report Download */}
                {m.reportUrl && (
                  <a
                    href={m.reportUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 mt-3 text-xs bg-zinc-800 hover:bg-zinc-700 text-cyan-400 border border-zinc-700 px-3.5 py-2 rounded-lg font-medium transition-all"
                  >
                    <FileText size={14} /> Download PDF Report
                  </a>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-sm text-zinc-500 italic">Executing workflow nodes...</div>}
        </div>

        {/* Input container */}
        <form onSubmit={handleSend} className="p-6 border-t border-zinc-800 flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl px-5 py-3.5 text-zinc-300 focus:outline-none focus:border-cyan-500 transition-all text-sm"
          />
          <button type="submit" className="w-12 h-12 bg-cyan-600 hover:bg-cyan-500 rounded-xl flex items-center justify-center text-white transition-all">
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};
