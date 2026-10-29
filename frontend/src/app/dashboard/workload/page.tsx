"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getWorkloadAlerts } from "@/lib/api";
import {
  Bell,
  AlertTriangle,
  ShieldAlert,
  Zap,
  Activity,
  CheckCircle2,
  CalendarCheck,
  TrendingUp,
  RefreshCw,
  HeartPulse
} from "lucide-react";

export default function WorkloadAlertsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [resolvedIds, setResolvedIds] = useState<number[]>([]);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const res = await getWorkloadAlerts(token);
      setData(res);
    } catch (err) {
      console.error("Failed to load workload alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResolveAlert = (id: number) => {
    setResolvedIds((prev) => [...prev, id]);
  };

  const activeAlerts = (data?.alerts || []).filter(
    (a: any) => !resolvedIds.includes(a.id)
  );

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-semibold uppercase tracking-wider">
              Workload &amp; Fatigue Advisory
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">
            Workload Alerts &amp; ACWR Monitoring
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Acute-to-Chronic Workload Ratio (ACWR) tracking, training volume spikes, and overuse injury early warnings.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 rounded-xl text-xs font-bold transition-all flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-rose-400" : ""}`} />
          <span>Sync Telemetry</span>
        </button>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Team ACWR Index</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-white">{data?.team_acwr_average ?? "1.28"}</span>
            <span className="text-xs text-slate-500">Ratio</span>
          </div>
          <div className="text-[11px] text-emerald-400 font-semibold mt-1">
            {data?.status || "Optimal Range (0.8 - 1.3)"}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>Active Workload Warnings</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-rose-400">{activeAlerts.length}</span>
            <span className="text-xs text-slate-500">Unresolved Flags</span>
          </div>
          <div className="text-[11px] text-slate-400 font-medium mt-1">
            Deload recommendations generated
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
            <HeartPulse className="w-4 h-4 text-indigo-400" />
            <span>Overuse Injury Prevention</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-white">94%</span>
            <span className="text-xs text-slate-500">Protected</span>
          </div>
          <div className="text-[11px] text-indigo-300 font-medium mt-1">
            Early detection active across team
          </div>
        </div>
      </div>

      {/* Active Alerts List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-rose-400" />
            <span>Active Clinical Workload Flags ({activeAlerts.length})</span>
          </h3>
          {resolvedIds.length > 0 && (
            <button
              onClick={() => setResolvedIds([])}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-bold cursor-pointer"
            >
              Reset Resolved ({resolvedIds.length})
            </button>
          )}
        </div>

        {activeAlerts.length === 0 ? (
          <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">All Workload Flags Resolved</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              All athletes are currently operating within the safe physiological training threshold. Continue routine monitoring.
            </p>
          </div>
        ) : (
          activeAlerts.map((alert: any) => (
            <div
              key={alert.id}
              className={`glass-panel p-5 rounded-2xl border relative overflow-hidden transition-all ${alert.severity === "Critical"
                ? "border-rose-500/40 bg-rose-950/20"
                : alert.severity === "Warning"
                  ? "border-amber-500/40 bg-amber-950/20"
                  : "border-slate-800 bg-slate-950/60"
                }`}
            >
              <div
                className={`absolute top-0 left-0 w-2 h-full ${alert.severity === "Critical"
                  ? "bg-rose-500"
                  : alert.severity === "Warning"
                    ? "bg-amber-500"
                    : "bg-indigo-500"
                  }`}
              />

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pl-3">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border ${alert.severity === "Critical"
                        ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                        : alert.severity === "Warning"
                          ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                          : "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"
                        }`}
                    >
                      {alert.severity} Flag
                    </span>
                    <span className="text-sm font-bold text-white">{alert.athlete_name}</span>
                    <span className="text-xs text-slate-400">•</span>
                    <span className="text-xs font-mono text-indigo-300">{alert.metric}: {alert.value}</span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    {alert.description}
                  </p>

                  <div className="text-xs text-slate-200 bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <strong className="text-indigo-400">Recommended Intervention: </strong>
                    <span>{alert.recommended_action}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
                  <Link
                    href="/dashboard/training"
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_12px_rgba(99,102,241,0.3)] inline-flex items-center gap-1.5"
                  >
                    <CalendarCheck className="w-3.5 h-3.5" />
                    <span>Prescribe Deload</span>
                  </Link>
                  <button
                    onClick={() => handleResolveAlert(alert.id)}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-semibold transition-colors cursor-pointer"
                  >
                    Resolve
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
