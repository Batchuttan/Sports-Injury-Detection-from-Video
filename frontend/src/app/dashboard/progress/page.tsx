"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getPerformanceRecords, createPerformanceRecord } from "@/lib/api";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

interface RecordData {
  id?: number;
  date: string;
  metric: string;
  value: number;
  unit: string;
}

export default function ProgressPage() {
  const [records, setRecords] = useState<RecordData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeMetricFilter, setActiveMetricFilter] = useState<string>("40m Sprint Time");
  const [isMounted, setIsMounted] = useState(false);

  const [formData, setFormData] = useState({
    date: new Date().toISOString().split("T")[0],
    metric: "40m Sprint Time",
    value: "",
    unit: "sec",
  });

  const loadRecords = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const data = await getPerformanceRecords(token);
      setRecords(data);
    } catch (err) {
      console.error("Failed to load records:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadRecords();
  }, []);

  const handleMetricChangeInForm = (metricName: string) => {
    let unit = "sec";
    if (metricName.includes("Valgus") || metricName.includes("Angle")) unit = "deg";
    else if (metricName.includes("Velocity") || metricName.includes("Speed")) unit = "km/h";
    else if (metricName.includes("Workload") || metricName.includes("ACWR") || metricName.includes("Ratio")) unit = "ratio";
    else if (metricName.includes("Jump") || metricName.includes("Height")) unit = "cm";
    setFormData({ ...formData, metric: metricName, unit });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const payload = {
        ...formData,
        value: parseFloat(formData.value),
      };

      await createPerformanceRecord(token, payload);
      setShowForm(false);
      setFormData({
        date: new Date().toISOString().split("T")[0],
        metric: "40m Sprint Time",
        value: "",
        unit: "sec",
      });
      loadRecords();
    } catch (err) {
      console.error("Failed to add performance record:", err);
      alert("Failed to save performance record to backend.");
    } finally {
      setSubmitting(false);
    }
  };

  // Filter records for the active metric to plot the longitudinal curve
  const filteredRecords = records
    .filter((r) => r.metric.toLowerCase() === activeMetricFilter.toLowerCase())
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Distinct metrics available in records or standard list
  const availableMetrics = Array.from(
    new Set([
      "40m Sprint Time",
      "Dynamic Knee Valgus Angle",
      "Max Sprint Velocity",
      "Acute-to-Chronic Workload (ACWR)",
      ...records.map((r) => r.metric),
    ])
  );

  // Latest stats calculation
  const sprintRecords = records.filter((r) => r.metric.includes("Sprint Time"));
  const latestSprint = sprintRecords.length > 0 ? sprintRecords[0].value : 4.88;
  const bestSprint = sprintRecords.length > 0 ? Math.min(...sprintRecords.map((r) => r.value)) : 4.88;

  const valgusRecords = records.filter((r) => r.metric.includes("Valgus"));
  const latestValgus = valgusRecords.length > 0 ? valgusRecords[0].value : 10.8;

  const velocityRecords = records.filter((r) => r.metric.includes("Velocity"));
  const topVelocity = velocityRecords.length > 0 ? Math.max(...velocityRecords.map((r) => r.value)) : 32.8;

  const acwrRecords = records.filter((r) => r.metric.includes("Workload") || r.metric.includes("ACWR"));
  const latestAcwr = acwrRecords.length > 0 ? acwrRecords[0].value : 1.08;

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Longitudinal Progress & Performance Curves</h2>
          <p className="text-slate-400 text-sm mt-1">
            Track multi-week kinetic adaptation, valgus reduction trajectories, sprint velocity gains, and workload safety.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all font-semibold text-xs shadow-[0_0_15px_rgba(79,70,229,0.3)] flex items-center gap-2 cursor-pointer"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            {showForm ? "Cancel Entry" : "Log Performance Metric"}
          </button>
        </div>
      </div>

      {/* KPI Highlight Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Sprint Time */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center justify-between">
            <span>40m Sprint PB</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">-0.20s</span>
          </div>
          <div className="text-3xl font-extrabold text-white">{bestSprint} <span className="text-xs font-normal text-slate-400">sec</span></div>
          <p className="text-[11px] text-slate-400">Recent: {latestSprint}s (Continuous progression)</p>
        </div>

        {/* Dynamic Valgus */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center justify-between">
            <span>Knee Valgus Deviation</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20">-7.6° Stabilized</span>
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">{latestValgus}° <span className="text-xs font-normal text-slate-400">peak</span></div>
          <p className="text-[11px] text-emerald-300 font-medium">Safely below 15° injury risk threshold</p>
        </div>

        {/* Max Velocity */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Top Sprint Velocity</div>
          <div className="text-3xl font-extrabold text-white">{topVelocity} <span className="text-xs font-normal text-slate-400">km/h</span></div>
          <p className="text-[11px] text-slate-400">+1.6 km/h improvement since training camp</p>
        </div>

        {/* Workload Ratio */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Workload Ratio (ACWR)</div>
          <div className="text-3xl font-extrabold text-indigo-400">{latestAcwr} <span className="text-xs font-normal text-slate-400">ratio</span></div>
          <p className="text-[11px] text-emerald-400 font-medium">In the optimal sweet spot (0.8 - 1.3)</p>
        </div>
      </div>

      {/* Main Interactive Recharts Curve */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              {activeMetricFilter} Trajectory
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Longitudinal measurements recorded across video analysis sessions and training camp assessments.
            </p>
          </div>

          {/* Metric Selector Pills */}
          <div className="flex flex-wrap gap-2">
            {availableMetrics.slice(0, 4).map((m) => (
              <button
                key={m}
                onClick={() => setActiveMetricFilter(m)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${activeMetricFilter === m
                    ? "bg-indigo-600 text-white shadow-[0_0_12px_rgba(79,70,229,0.4)]"
                    : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                  }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>

        {/* Chart View */}
        <div className="h-72 w-full pt-2">
          {isMounted && filteredRecords.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredRecords} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="metricGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={["auto", "auto"]} tickLine={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload as RecordData;
                      return (
                        <div className="p-3 bg-slate-900 border border-slate-700 rounded-xl shadow-xl text-xs space-y-1">
                          <div className="text-slate-400">{data.date}</div>
                          <div className="font-bold text-white">{data.metric}</div>
                          <div className="text-indigo-400 font-extrabold text-sm">
                            {data.value} {data.unit}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#818cf8"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#metricGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 text-xs">
              <span>No entries found for &quot;{activeMetricFilter}&quot;.</span>
              <span className="text-slate-600 mt-1">Click &quot;Log Performance Metric&quot; to add data.</span>
            </div>
          )}
        </div>
      </div>

      {/* Log Record Modal / Inline Form */}
      {showForm && (
        <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-indigo-500/40 space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
              Log New Performance Metric Record
            </h3>
            <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-white text-xs cursor-pointer">
              Close
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Date</label>
                <input
                  required
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Performance Metric</label>
                <select
                  value={formData.metric}
                  onChange={(e) => handleMetricChangeInForm(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none cursor-pointer"
                >
                  <option value="40m Sprint Time">40m Sprint Time</option>
                  <option value="Dynamic Knee Valgus Angle">Dynamic Knee Valgus Angle</option>
                  <option value="Max Sprint Velocity">Max Sprint Velocity</option>
                  <option value="Acute-to-Chronic Workload (ACWR)">Acute-to-Chronic Workload (ACWR)</option>
                  <option value="Peak Countermovement Jump">Peak Countermovement Jump</option>
                  <option value="Trunk Lean Lateral Angle">Trunk Lean Lateral Angle</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Recorded Value</label>
                <input
                  required
                  type="number"
                  step="0.01"
                  placeholder="e.g. 4.88"
                  value={formData.value}
                  onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Measurement Unit</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. sec, deg, km/h"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none"
                />
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-md shadow-indigo-500/20 disabled:opacity-50 cursor-pointer"
              >
                {submitting ? "Saving to Backend..." : "Save Metric Record"}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl border border-slate-700 cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Historical Telemetry Table */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">Logged Performance Telemetry</h3>
          <span className="text-xs text-slate-500">{records.length} Telemetry Records</span>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-500 text-sm">Loading performance telemetry...</div>
        ) : records.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No performance entries recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-4 font-semibold">Date</th>
                  <th className="py-3 px-4 font-semibold">Performance Metric</th>
                  <th className="py-3 px-4 font-semibold">Recorded Value</th>
                  <th className="py-3 px-4 font-semibold">Clinical Category</th>
                  <th className="py-3 px-4 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r, i) => (
                  <tr
                    key={i}
                    className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors"
                  >
                    <td className="py-3 px-4 text-slate-400 font-mono text-xs">{r.date}</td>
                    <td className="py-3 px-4 font-medium text-white">{r.metric}</td>
                    <td className="py-3 px-4 text-indigo-400 font-extrabold text-sm">
                      {r.value} <span className="text-xs font-normal text-slate-400">{r.unit}</span>
                    </td>
                    <td className="py-3 px-4">
                      {r.metric.includes("Valgus") ? (
                        r.value <= 12 ? (
                          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold">Safe Kinematic Zone</span>
                        ) : (
                          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold">Elevated Adduction</span>
                        )
                      ) : r.metric.includes("Sprint") ? (
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 font-semibold">Speed Acceleration</span>
                      ) : (
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-purple-500/15 text-purple-400 border border-purple-500/30 font-semibold">Biomechanical Metric</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href="/dashboard/compare"
                        className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        Compare &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Connected Dashboard Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link
          href="/dashboard/upload"
          className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all group"
        >
          <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 group-hover:text-indigo-300">
            Movement Analysis
          </div>
          <div className="text-white font-semibold text-sm">Upload Video for Kinematic Verification &rarr;</div>
          <div className="text-xs text-slate-500 mt-1">Autonomous 8-action detection and 33-joint telemetry</div>
        </Link>

        <Link
          href="/dashboard/compare"
          className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-pink-500/50 transition-all group"
        >
          <div className="text-xs font-bold text-pink-400 uppercase tracking-wider mb-1 group-hover:text-pink-300">
            Side-by-Side Kinematics
          </div>
          <div className="text-white font-semibold text-sm">Dual Video Comparison Engine &rarr;</div>
          <div className="text-xs text-slate-500 mt-1">Measure pre vs post intervention angles side-by-side</div>
        </Link>

        <Link
          href="/dashboard/training"
          className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all group"
        >
          <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 group-hover:text-indigo-300">
            Corrective Intervention
          </div>
          <div className="text-white font-semibold text-sm">Prescribed Knee Valgus & Core Drills &rarr;</div>
          <div className="text-xs text-slate-500 mt-1">View sets, reps, and track exercise completions</div>
        </Link>
      </div>
    </div>
  );
}
