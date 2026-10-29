"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getTeamMonitoring } from "@/lib/api";
import {
  Users,
  Search,
  Filter,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Activity,
  ArrowRight,
  TrendingDown,
  UserCheck,
  RefreshCw,
  Eye,
  CalendarCheck
} from "lucide-react";

export default function PlayerMonitoringPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const res = await getTeamMonitoring(token);
      setData(res);
    } catch (err) {
      console.error("Failed to load team monitoring:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const roster = data?.athlete_roster || [];
  const filteredRoster = roster.filter((athlete: any) => {
    const matchesSearch =
      athlete.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      athlete.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      athlete.sport.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "All" || athlete.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold uppercase tracking-wider">
              Coach &amp; Technical Staff
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">
            Player Monitoring &amp; Team Roster
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time biomechanical injury risk profiling, acute workload status, and athlete readiness tracking.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 rounded-xl text-xs font-bold transition-all flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          <span>Refresh Roster</span>
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Team Overall Risk Score</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-white">{data?.team_overall_risk_score ?? 28}</span>
            <span className="text-xs text-slate-500">/ 100 Risk</span>
          </div>
          <div className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1 mt-1">
            <TrendingDown className="w-3.5 h-3.5" />
            <span>Optimal Baseline (-8% from last cycle)</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Roster Size</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-white">{data?.total_athletes ?? 0}</span>
            <span className="text-xs text-slate-500">Registered Athletes</span>
          </div>
          <div className="text-[11px] text-indigo-400 font-semibold mt-1">
            100% Biomechanical Coverage
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>High Risk / Restricted</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-rose-400">{data?.high_risk_count ?? 0}</span>
            <span className="text-xs text-slate-500">Athletes Flagged</span>
          </div>
          <div className="text-[11px] text-rose-300 font-medium mt-1">
            Requires training modification
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Cleared for Competition</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-emerald-400">{data?.low_risk_count ?? 0}</span>
            <span className="text-xs text-slate-500">Full Form Readiness</span>
          </div>
          <div className="text-[11px] text-slate-400 font-medium mt-1">
            Low Valgus &amp; Kinetic Symmetry
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search athlete by name, email, sport..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs text-slate-400 font-medium">Status:</span>
          {["All", "Cleared to Play", "Under Observation", "Restricted"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${statusFilter === st
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Roster Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-bold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Athlete</th>
                <th className="py-3.5 px-4">Sport &amp; Position</th>
                <th className="py-3.5 px-4">Latest Action</th>
                <th className="py-3.5 px-4">Injury Risk Score</th>
                <th className="py-3.5 px-4">Clearance Status</th>
                <th className="py-3.5 px-4">Last Assessment</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {filteredRoster.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                    No athletes matching your criteria.
                  </td>
                </tr>
              ) : (
                filteredRoster.map((athlete: any) => (
                  <tr key={athlete.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-600 to-pink-600 flex items-center justify-center font-black text-white text-xs shrink-0">
                          {athlete.name.slice(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-bold text-white text-sm">{athlete.name}</div>
                          <div className="text-[11px] text-slate-500 font-mono">{athlete.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="text-white font-medium">{athlete.sport}</div>
                      <div className="text-[11px] text-slate-500">{athlete.position}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[11px] text-indigo-300 font-semibold">
                        {athlete.latest_activity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <span
                          className={`font-black text-sm ${athlete.risk_score > 35
                              ? "text-rose-400"
                              : athlete.risk_score > 20
                                ? "text-amber-400"
                                : "text-emerald-400"
                            }`}
                        >
                          {athlete.risk_score} / 100
                        </span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${athlete.risk_score > 35
                              ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                              : athlete.risk_score > 20
                                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            }`}
                        >
                          {athlete.risk_level}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border ${athlete.status === "Cleared to Play"
                            ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                            : athlete.status === "Under Observation"
                              ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                              : "bg-rose-500/15 text-rose-400 border-rose-500/30"
                          }`}
                      >
                        {athlete.status === "Cleared to Play" ? (
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        ) : athlete.status === "Under Observation" ? (
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                        ) : (
                          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                        )}
                        <span>{athlete.status}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {athlete.last_assessed}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href="/dashboard/reports"
                          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-indigo-300 hover:text-white rounded-lg border border-slate-800 text-[11px] font-bold transition-colors inline-flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3" />
                          <span>Reports</span>
                        </Link>
                        <Link
                          href="/dashboard/training"
                          className="px-2.5 py-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 hover:text-white rounded-lg border border-indigo-500/30 text-[11px] font-bold transition-colors inline-flex items-center gap-1"
                        >
                          <CalendarCheck className="w-3 h-3" />
                          <span>Plan</span>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
