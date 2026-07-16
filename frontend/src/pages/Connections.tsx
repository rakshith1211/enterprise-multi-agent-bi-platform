import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Plus, Trash } from "lucide-react";

export const Connections: React.FC = () => {
  const [conns, setConns] = useState<any[]>([]);
  const [name, setName] = useState("");
  const [dbType, setDbType] = useState("sqlite");
  const [dbName, setDbName] = useState(":memory:");
  const [env, setEnv] = useState("Development");

  const fetchConns = () => {
    api.get("/connections").then((res) => setConns(res.data));
  };

  useEffect(() => {
    fetchConns();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/connections", {
        name,
        database_type: dbType,
        database_name: dbName,
        environment: env,
      });
      setName("");
      setDbName(":memory:");
      fetchConns();
    } catch (err) {
      console.error("Connection creation failed", err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/connections/${id}`);
      fetchConns();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">Database Connections</h1>
        <p className="text-zinc-500 text-sm mt-1">Configure active relational and analytical data adapters</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form connector */}
        <div className="lg:col-span-1 bg-zinc-900/50 border border-zinc-800 p-6 rounded-xl space-y-5">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <Plus size={18} className="text-cyan-400" /> Create Adapter Profile
          </h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">Profile Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Sales Production DB"
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">Engine Type</label>
              <select
                value={dbType}
                onChange={(e) => setDbType(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 text-zinc-300"
              >
                <option value="sqlite">SQLite</option>
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="duckdb">DuckDB</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">Database Name / Path</label>
              <input
                type="text"
                value={dbName}
                onChange={(e) => setDbName(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 font-mono"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-zinc-400 uppercase mb-1.5">Environment</label>
              <select
                value={env}
                onChange={(e) => setEnv(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 text-zinc-300"
              >
                <option value="Development">Development</option>
                <option value="Staging">Staging</option>
                <option value="Production">Production</option>
              </select>
            </div>
            <button
              type="submit"
              className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 rounded text-sm font-semibold transition-all"
            >
              Save Connector
            </button>
          </form>
        </div>

        {/* Connections List */}
        <div className="lg:col-span-2 bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-semibold">
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Dialect</th>
                <th className="px-6 py-4">Database</th>
                <th className="px-6 py-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {conns.map((row) => (
                <tr key={row.id} className="hover:bg-zinc-800/30 transition-all">
                  <td className="px-6 py-4 font-semibold text-zinc-300">{row.name}</td>
                  <td className="px-6 py-4 text-cyan-400 uppercase text-xs font-bold">{row.database_type}</td>
                  <td className="px-6 py-4 font-mono text-xs">{row.database_name}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleDelete(row.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              {conns.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center py-8 text-zinc-500">No database connections configured.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
