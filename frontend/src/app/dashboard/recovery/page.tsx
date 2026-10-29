"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getRecoveryStatus } from "@/lib/api";
import {
  ShieldCheck,
  Activity,
  HeartPulse,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  RefreshCw,
  CalendarCheck,
  Stethoscope,
  Clock,
  ArrowRight
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";

export default function RecoveryStatusPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const res = await getRecoveryStatus(token);
      setData(res);
    } catch (err) {
      console.error("Failed to load recovery status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const trends = data?.injury_recovery_trends || [];
  const patients = data?.rehab_patients || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/30 font-semibold uppercase tracking-wider">
              Physiotherapist &amp; Medical Team
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">
            Rehabilitation &amp; Recovery Status
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Clinical return-to-play tracking, active injury protocols, and joint range of motion (ROM) restoration.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 rounded-xl text-xs font-bold transition-all flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-teal-400" : ""}`} />
          <span>Refresh Clinical Data</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            <span>Active Injuries Under Care</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-rose-400">{data?.active_injuries_count ?? 4}</span>
            <span className="text-xs text-slate-500">Athletes</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Under active physical therapy supervision
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-indigo-400" />
            <span>Active Rehab Protocols</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-white">{data?.rehab_plans_active ?? 12}</span>
            <span className="text-xs text-slate-500">Plans Running</span>
          </div>
          <div className="text-[11px] text-indigo-300 mt-1">
            Neuromuscular &amp; eccentric loading protocols
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Cleared to Play (This Week)</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-emerald-400">{data?.cleared_this_week ?? 3}</span>
            <span className="text-xs text-slate-500">Athletes</span>
          </div>
          <div className="text-[11px] text-emerald-400 font-semibold mt-1">
            Passed functional biomechanics battery
          </div>
        </div>
      </div>

      {/* Injury vs Recovery Trends Chart */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-teal-400" />
            <span>7-Day Injury Incidence vs. Clinical Recovery Trends</span>
          </h3>
          <span className="text-xs font-mono text-slate-400">Weekly Clinical Matrix</span>
        </div>

        <div className="h-64 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" textAnchor="end" fontSize={11} />
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
              <Bar dataKey="injuries" fill="#f43f5e" name="New Injury Flags" radius={[4, 4, 0, 0]} />
              <Bar dataKey="recoveries" fill="#10b981" name="Completed Rehabilitations" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Active Rehabilitation Patient Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden space-y-3 p-5">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Stethoscope className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">Active Athlete Rehabilitation Roster</h3>
          </div>
          <Link
            href="/dashboard/training"
            className="text-xs text-indigo-400 hover:text-indigo-300 font-bold inline-flex items-center gap-1"
          >
            <span>Manage All 7 Plans</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-3 pt-1">
          {patients.map((patient: any) => (
            <div
              key={patient.id}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white text-sm">{patient.athlete_name}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                    {patient.target_joint}
                  </span>
                </div>
                <div className="text-xs text-rose-300 font-medium">
                  Diagnosis: {patient.injury}
                </div>
                <div className="text-xs text-slate-400">
                  Protocol: <strong className="text-indigo-300">{patient.protocol}</strong> ({patient.clearance_phase})
                </div>
              </div>

              <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end">
                <div className="text-right">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Restoration Progress</div>
                  <div className="text-lg font-black text-white">{patient.completion_percent}%</div>
                  <div className="text-[11px] font-mono text-teal-400">{patient.rom_degrees}</div>
                </div>

                <div className="w-24 bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${patient.completion_percent === 100
                        ? "bg-emerald-400"
                        : "bg-gradient-to-r from-teal-500 to-indigo-500"
                      }`}
                    style={{ width: `${patient.completion_percent}%` }}
                  />
                </div>

                <span
                  className={`text-xs px-2.5 py-1 rounded-xl font-bold border shrink-0 ${patient.status === "Cleared to Play"
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                      : "bg-teal-500/20 text-teal-300 border-teal-500/30"
                    }`}
                >
                  {patient.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
