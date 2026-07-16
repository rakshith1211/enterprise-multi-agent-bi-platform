import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Upload, Trash2 } from "lucide-react";

export const Documents: React.FC = () => {
  const [docs, setDocs] = useState<any[]>([]);
  const [docName, setDocName] = useState("");
  const [docType, setDocType] = useState("md");
  const [textContent, setTextContent] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchDocs = () => {
    api.get("/rag/history").then((res) => setDocs(res.data));
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docName.trim() || !textContent.trim()) return;

    setLoading(true);
    try {
      await api.post("/rag/ingest", {
        document_name: docName,
        file_type: docType,
        text_content: textContent,
        metadata: {
          author: "system",
          permissions: "public"
        }
      });
      setDocName("");
      setTextContent("");
      fetchDocs();
    } catch (err) {
      console.error("Ingestion failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/rag/document/${id}`);
      fetchDocs();
    } catch (err) {
      console.error("Deletion failed", err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">RAG Knowledge Base Documents</h1>
        <p className="text-zinc-500 text-sm mt-1">Ingest unstructured files to build semantic indexes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload form */}
        <div className="lg:col-span-1 bg-zinc-900/50 border border-zinc-800 p-6 rounded-xl space-y-5">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <Upload size={18} className="text-cyan-400" /> Ingest New Document
          </h3>
          <form onSubmit={handleIngest} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">Document Name</label>
              <input
                type="text"
                value={docName}
                onChange={(e) => setDocName(e.target.value)}
                placeholder="e.g. refund_policies.md"
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">File Type</label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 text-zinc-300"
              >
                <option value="md">Markdown (.md)</option>
                <option value="txt">Text (.txt)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="docx">Word (.docx)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">Content Text</label>
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                rows={5}
                placeholder="Paste document body context..."
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 font-mono text-xs"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 rounded text-sm font-semibold transition-all shadow-[0_0_15px_rgba(6,182,212,0.1)]"
            >
              {loading ? "Indexing..." : "Ingest Document"}
            </button>
          </form>
        </div>

        {/* Documents Table List */}
        <div className="lg:col-span-2 bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-semibold">
                <th className="px-6 py-4">Document Name</th>
                <th className="px-6 py-4">Chunks</th>
                <th className="px-6 py-4">Version</th>
                <th className="px-6 py-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {docs.map((row) => (
                <tr key={row.id} className="hover:bg-zinc-800/30 transition-all">
                  <td className="px-6 py-4 font-medium text-zinc-300">{row.document_name}</td>
                  <td className="px-6 py-4 text-cyan-400 font-medium">{row.chunks_count} chunks</td>
                  <td className="px-6 py-4">v{row.doc_version}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleDelete(row.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              {docs.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center py-8 text-zinc-500">No RAG corpus ingested.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
