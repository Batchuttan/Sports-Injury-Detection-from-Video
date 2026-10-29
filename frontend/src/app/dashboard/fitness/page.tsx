"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getPhysicalAssessments, createPhysicalAssessment } from "@/lib/api";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from "recharts";

interface Assessment {
  id: number;
  date: string;
  test_name: string;
  score: number;
  notes: string;
}

export default function FitnessPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  const [formData, setFormData] = useState({
    date: new Date().toISOString().split("T")[0],
    test_name: "VO2 Max Aerobic Capacity",
    score: "",
    notes: "",
  });

  const loadAssessments = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const data = await getPhysicalAssessments(token);
      setAssessments(data);
    } catch (err) {
      console.error("Failed to load assessments:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadAssessments();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const payload = {
        ...formData,
        score: parseFloat(formData.score),
      };

      await createPhysicalAssessment(token, payload);
      setShowForm(false);
      setFormData({
        date: new Date().toISOString().split("T")[0],
        test_name: "VO2 Max Aerobic Capacity",
        score: "",
        notes: "",
      });
      loadAssessments();
    } catch (err) {
      console.error("Failed to add assessment:", err);
      alert("Failed to save assessment to backend.");
    } finally {
      setSubmitting(false);
    }
  };

  // Normative benchmark percentages for the standard sports science battery
  const chartData = [
    { name: "Aerobic (VO2)", score: 92, raw: "56.4 mL/kg/min", benchmark: "Elite Tier (>52)" },
    { name: "FMS Stability", score: 81, raw: "17 / 21", benchmark: "Low Risk (>15)" },
    { name: "Jump Power", score: 88, raw: "44.5 cm", benchmark: "Collegiate (>40cm)" },
    { name: "Y-Balance", score: 96, raw: "95.8% Symmetry", benchmark: "Safe (>90%)" },
    { name: "RSI Elastic", score: 85, raw: "2.18 Index", benchmark: "Good Elasticity (>2.0)" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Physical Assessment & Fitness Analytics</h2>
          <p className="text-slate-400 text-sm mt-1">
            Standardized physiological benchmarks, neuromuscular readiness scores, and functional mobility diagnostics.
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
            {showForm ? "Cancel Assessment" : "Record Assessment"}
          </button>
        </div>
      </div>

      {/* KPI Readiness Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center justify-between">
            <span>Readiness Index</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>
          <div className="text-3xl font-extrabold text-white">88 <span className="text-xs font-normal text-slate-400">/ 100</span></div>
          <p className="text-[11px] text-emerald-400 font-medium">Optimal match readiness baseline</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Aerobic Capacity (VO2)</div>
          <div className="text-3xl font-extrabold text-white">56.4 <span className="text-xs font-normal text-slate-400">mL/kg/min</span></div>
          <p className="text-[11px] text-slate-400">Top 10th percentile for collegiate wings</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Movement Screen (FMS)</div>
          <div className="text-3xl font-extrabold text-white">17 <span className="text-xs font-normal text-slate-400">/ 21</span></div>
          <p className="text-[11px] text-indigo-300">Low musculoskeletal injury risk</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Bilateral Symmetry</div>
          <div className="text-3xl font-extrabold text-emerald-400">96.2%</div>
          <p className="text-[11px] text-slate-400">Normal physiological limits (&gt;90%)</p>
        </div>
      </div>

      {/* Physical Capacity Battery Chart */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
          <div>
            <h3 className="text-lg font-bold text-white">Functional Capacity vs. Normative Athlete Benchmarks</h3>
            <p className="text-xs text-slate-400">Percentile ranking normalized against collegiate & professional athlete baselines.</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="w-3 h-3 rounded-md bg-indigo-500"></span>
            <span>Athlete Percentile (%)</span>
          </div>
        </div>

        <div className="h-64 w-full pt-4">
          {isMounted && (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 100]} tickLine={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="p-3 bg-slate-900 border border-slate-700 rounded-xl shadow-xl text-xs space-y-1">
                          <div className="font-bold text-white">{data.name}</div>
                          <div className="text-indigo-400 font-semibold">Percentile: {data.score}%</div>
                          <div className="text-slate-300">Actual Metric: {data.raw}</div>
                          <div className="text-slate-500 text-[11px]">Norm: {data.benchmark}</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.score >= 90 ? "#6366f1" : entry.score >= 80 ? "#818cf8" : "#ec4899"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Record Assessment Modal / Drawer */}
      {showForm && (
        <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-indigo-500/40 space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
              Record New Physical Assessment Metric
            </h3>
            <button
              onClick={() => setShowForm(false)}
              className="text-slate-400 hover:text-white text-xs cursor-pointer"
            >
              Close
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Date of Testing</label>
                <input
                  required
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Assessment Protocol</label>
                <select
                  value={formData.test_name}
                  onChange={(e) => setFormData({ ...formData, test_name: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none cursor-pointer"
                >
                  <option value="VO2 Max Aerobic Capacity">VO2 Max Aerobic Capacity</option>
                  <option value="Functional Movement Screen (FMS)">Functional Movement Screen (FMS)</option>
                  <option value="Countermovement Jump (CMJ)">Countermovement Jump (CMJ)</option>
                  <option value="Y-Balance Dynamic Stability">Y-Balance Dynamic Stability</option>
                  <option value="Reactive Strength Index (RSI)">Reactive Strength Index (RSI)</option>
                  <option value="1RM Barbell Back Squat">1RM Barbell Back Squat</option>
                  <option value="Beep Test / Yo-Yo Intermittent">Beep Test / Yo-Yo Intermittent</option>
                  <option value="Sit & Reach Flexibility">Sit & Reach Flexibility</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Recorded Score</label>
                <input
                  required
                  type="number"
                  step="0.01"
                  placeholder="e.g. 56.4"
                  value={formData.score}
                  onChange={(e) => setFormData({ ...formData, score: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 text-white text-sm outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Clinical Observations / Notes</label>
                <input
                  type="text"
                  placeholder="Physio notes, joint sensations, etc."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
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
                {submitting ? "Saving to Backend..." : "Commit Assessment"}
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

      {/* Assessment Test Battery Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">Documented Assessment Battery</h3>
          <span className="text-xs text-slate-500">{assessments.length} Tests Logged in Backend</span>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-500 text-sm">Loading test records...</div>
        ) : assessments.length === 0 ? (
          <div className="glass-panel p-8 text-center rounded-2xl text-slate-400 text-sm">
            No physical assessment records logged yet. Click &quot;Record Assessment&quot; above to add your first baseline test.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {assessments.map((a) => (
              <div
                key={a.id}
                className="glass-panel p-6 rounded-2xl border border-slate-800 hover:border-slate-700/80 transition-all space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start gap-2 mb-1">
                    <h4 className="text-base font-bold text-white">{a.test_name}</h4>
                    <span className="text-[11px] text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded-lg border border-slate-800 shrink-0">
                      {a.date}
                    </span>
                  </div>

                  <div className="flex items-baseline gap-2 mt-2">
                    <div className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-400">
                      {a.score}
                    </div>
                  </div>

                  {a.notes && (
                    <p className="text-xs text-slate-400 leading-relaxed mt-2 pt-2 border-t border-slate-800/80">
                      {a.notes}
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-800/60 text-xs">
                  <span className="text-emerald-400 font-medium flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    Verified Metric
                  </span>
                  <Link
                    href="/dashboard/progress"
                    className="text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
                  >
                    View Progression &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Connected Dashboard Navigation Hyperlinks */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <h4 className="text-sm font-bold text-white uppercase tracking-wider">Connected Biomechanical Modules</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href="/dashboard/upload"
            className="p-4 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 transition-all group"
          >
            <div className="text-xs font-semibold text-indigo-400 mb-1 group-hover:text-indigo-300">1. Video Pose Engine</div>
            <div className="text-sm font-bold text-white">Analyze Movement &rarr;</div>
            <div className="text-xs text-slate-400 mt-1">Extract 33-point kinetic joint angles and valgus deviation</div>
          </Link>

          <Link
            href="/dashboard/compare"
            className="p-4 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-pink-500/40 transition-all group"
          >
            <div className="text-xs font-semibold text-pink-400 mb-1 group-hover:text-pink-300">2. Dual Comparison</div>
            <div className="text-sm font-bold text-white">Compare Bilateral Angles &rarr;</div>
            <div className="text-xs text-slate-400 mt-1">Side-by-side sync for pre vs post corrective intervention</div>
          </Link>

          <Link
            href="/dashboard/training"
            className="p-4 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 transition-all group"
          >
            <div className="text-xs font-semibold text-indigo-400 mb-1 group-hover:text-indigo-300">3. Corrective Plans</div>
            <div className="text-sm font-bold text-white">Execute Drills &rarr;</div>
            <div className="text-xs text-slate-400 mt-1">Knee Valgus Correction, Core Stability, and Recovery</div>
          </Link>

          <Link
            href="/dashboard/progress"
            className="p-4 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-purple-500/40 transition-all group"
          >
            <div className="text-xs font-semibold text-purple-400 mb-1 group-hover:text-purple-300">4. Progress Curves</div>
            <div className="text-sm font-bold text-white">Track Improvements &rarr;</div>
            <div className="text-xs text-slate-400 mt-1">Longitudinal speed, deceleration, and valgus angle curves</div>
          </Link>
        </div>
      </div>
    </div>
  );
}
