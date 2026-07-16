import React from "react";

export const Settings: React.FC = () => {
  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">System Settings</h1>
        <p className="text-zinc-500 text-sm mt-1">Configure workspace parameters and backend connections</p>
      </div>

      <div className="bg-zinc-900/30 border border-zinc-800 p-8 rounded-xl max-w-2xl space-y-6">
        <div className="space-y-2">
          <h3 className="font-bold text-lg text-zinc-300">Environment Metadata</h3>
          <p className="text-sm text-zinc-500">Status indicators for connected modules and databases.</p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between items-center py-3 border-b border-zinc-800">
            <span className="text-sm text-zinc-400 font-semibold">Backend Port</span>
            <span className="font-mono text-sm text-cyan-400">8000</span>
          </div>
          <div className="flex justify-between items-center py-3 border-b border-zinc-800">
            <span className="text-sm text-zinc-400 font-semibold">Primary Vector DB</span>
            <span className="font-mono text-sm text-cyan-400">ChromaDB</span>
          </div>
          <div className="flex justify-between items-center py-3 border-b border-zinc-800">
            <span className="text-sm text-zinc-400 font-semibold">Distributed Cache</span>
            <span className="font-mono text-sm text-cyan-400">Redis (Port 6379)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
