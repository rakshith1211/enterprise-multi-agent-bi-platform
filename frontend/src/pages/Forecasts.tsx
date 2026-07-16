import React, { useEffect, useState } from "react";
import { api } from "../lib/api";

export const Forecasts: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.get("/forecast/history").then((res) => setHistory(res.data));
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto text-zinc-100">
      <div>
        <h1 className="text-3xl font-extrabold">Time Series Forecasts</h1>
        <p className="text-zinc-500 text-sm mt-1">Benchmarks predictions and historical drift checks</p>
      </div>

      <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-semibold">
              <th className="px-6 py-4">ID</th>
              <th className="px-6 py-4">Selected Predictor</th>
              <th className="px-6 py-4">Validation MAPE</th>
              <th className="px-6 py-4">Drift Alert</th>
              <th className="px-6 py-4">Created At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {history.map((row) => (
              <tr key={row.id} className="hover:bg-zinc-800/30 transition-all">
                <td className="px-6 py-4 font-mono text-zinc-400 text-xs">{row.id}</td>
                <td className="px-6 py-4 font-medium text-emerald-400">{row.forecast_json?.selected_model || "ARIMA"}</td>
                <td className="px-6 py-4">{row.forecast_json?.mape ? `${row.forecast_json.mape.toFixed(2)}%` : "0.00%"}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${row.forecast_json?.drift_detected ? "bg-red-500/10 text-red-400" : "bg-green-500/10 text-green-400"}`}>
                    {row.forecast_json?.drift_detected ? "Drift Flagged" : "Stable"}
                  </span>
                </td>
                <td className="px-6 py-4 text-zinc-500">{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center py-8 text-zinc-500">No forecasting benchmarks run yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
