"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getScientistInsights } from "@/lib/api";
import {
  Compass,
  Sparkles,
  Activity,
  Layers,
  TrendingUp,
  Download,
  RefreshCw,
  PieChart as PieChartIcon,
  ShieldCheck,
  Zap,
  Target
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar
} from "recharts";

export default function BiomechanicalAnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const res = await getScientistInsights(token);
      setData(res);
    } catch (err) {
      console.error("Failed to load scientist insights:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const fatigueData = data?.fatigue_load_trends || [];
  const weightedModel = data?.weighted_scoring_model || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 font-semibold uppercase tracking-wider">
              Sports Scientist &amp; Biomechanist
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">
            Biomechanical Research &amp; Kinetic Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Predictive modeling weights, aggregate kinematic distributions, and fatigue-load interaction analysis.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 rounded-xl text-xs font-bold transition-all flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-violet-400" : ""}`} />
          <span>Refresh Insights</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Team Fatigue Index</div>
          <div className="text-xl font-black text-white mt-1">{data?.team_fatigue_index ?? "Normal Baseline"}</div>
          <div className="text-[11px] text-emerald-400 font-medium">Safe autonomic homeostasis</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Mean Valgus FPPA</div>
          <div className="text-2xl font-black text-indigo-400 mt-1">{data?.mean_valgus ?? 14.8}°</div>
          <div className="text-[11px] text-slate-400">Frontal plane knee alignment</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Mean Trunk Lean Sway</div>
          <div className="text-2xl font-black text-pink-400 mt-1">{data?.mean_trunk_sway ?? 18.2}°</div>
          <div className="text-[11px] text-slate-400">Sagittal / coronal sway</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Sessions Synthesized</div>
          <div className="text-2xl font-black text-white mt-1">{data?.total_sessions_analyzed ?? 0}</div>
          <div className="text-[11px] text-slate-400">Computer vision telemetry runs</div>
        </div>
      </div>

      {/* Training Load vs Fatigue Overlay Chart */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-violet-400" />
            <h3 className="text-base font-bold text-white">Rolling 7-Day Training Load vs. Neuromuscular Fatigue Overlay</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">Microcycle Synthesis</span>
        </div>

        <div className="h-64 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={fatigueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#020617",
                  borderColor: "#334155",
                  borderRadius: "0.75rem",
                  color: "#f8fafc",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
              <Line type="monotone" dataKey="load" stroke="#8b5cf6" strokeWidth={3} name="Cumulative Workload (AU)" />
              <Line type="monotone" dataKey="fatigue" stroke="#f59e0b" strokeWidth={3} name="Fatigue Biomarker Index" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Weighted Scoring Model Section (PDF Page 6 Exact Spec) */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="border-b border-slate-800/80 pb-3 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <PieChartIcon className="w-5 h-5 text-indigo-400" />
              <span>Weighted Injury Risk Mathematical Model (Module 8 Specification)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-factorial biomechanical weighting utilized to synthesize the unified Injury Risk Score (0-100)
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 font-mono font-bold">
            Σ = 100%
          </span>
        </div>

        <div className="space-y-3">
          {weightedModel.map((item: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white text-sm">{item.factor}</span>
                <span className="font-mono font-black text-indigo-400 text-sm">{item.weight}% Weight</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-pink-500 rounded-full"
                  style={{ width: `${item.weight * 2.5}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
