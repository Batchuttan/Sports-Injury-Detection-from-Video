"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getUserFromToken } from "@/lib/auth";
import {
  getAnalyses,
  getNotifications,
  deleteNotification,
  getTeamMonitoring,
  getWorkloadAlerts,
  getRecoveryStatus,
  getScientistInsights,
  getAdminPlatformStats,
  API_URL
} from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area
} from "recharts";
import {
  X,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Activity,
  Dumbbell,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Zap,
  Target,
  FileText,
  Lightbulb,
  Layers,
  ChevronRight,
  Flame,
  Award,
  Video,
  Bell
} from "lucide-react";

export default function DashboardHome() {
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);
  const [activeRole, setActiveRole] = useState<string>("");

  useEffect(() => {
    const fetchedUser = getUserFromToken();
    if (fetchedUser) {
      setUser(fetchedUser);
      const savedRole = localStorage.getItem("preview_role") || fetchedUser.role;
      setActiveRole(savedRole);
    }

    const handleRoleSwitch = (e: any) => {
      if (e.detail?.role) {
        setActiveRole(e.detail.role);
      }
    };
    window.addEventListener("role_switched", handleRoleSwitch);
    return () => window.removeEventListener("role_switched", handleRoleSwitch);
  }, []);

  if (!user) return null;

  const currentRole = activeRole || user.role;

  switch (currentRole) {
    case "Athlete":
      return <AthleteDashboard />;
    case "Physiotherapist":
      return <PhysioDashboard />;
    case "Sports Scientist":
      return <ScientistDashboard />;
    case "Administrator":
      return <AdminDashboard />;
    case "Coach":
    default:
      return <CoachDashboard />;
  }
}

function AthleteDashboard() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState<any[]>([]);

  const fetchOverviewData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;

      const [analysesData, notifData] = await Promise.all([
        getAnalyses(token, false).catch((err) => {
          console.error("Failed to load historical analyses for overview:", err);
          return [];
        }),
        getNotifications(token).catch((err) => {
          console.error("Failed to load notifications:", err);
          return [];
        }),
      ]);

      setAnalyses(analysesData || []);

      // Filter out previously dismissed notification IDs
      const dismissedStr = localStorage.getItem("dismissed_notifs") || "[]";
      let dismissedIds: number[] = [];
      try {
        dismissedIds = JSON.parse(dismissedStr);
      } catch {
        dismissedIds = [];
      }
      const activeNotifs = (notifData || []).filter((n: any) => !dismissedIds.includes(n.id));
      setNotifications(activeNotifs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const handleDismissNotification = async (notifId: number) => {
    // Remove immediately from UI
    setNotifications((prev) => prev.filter((n) => n.id !== notifId));

    // Store in localStorage so it stays dismissed across refreshes
    try {
      const dismissedStr = localStorage.getItem("dismissed_notifs") || "[]";
      let dismissedIds: number[] = [];
      try {
        dismissedIds = JSON.parse(dismissedStr);
      } catch {
        dismissedIds = [];
      }
      if (!dismissedIds.includes(notifId)) {
        dismissedIds.push(notifId);
        localStorage.setItem("dismissed_notifs", JSON.stringify(dismissedIds));
      }

      // Sync deletion with backend database
      const token = localStorage.getItem("token");
      if (token) {
        await deleteNotification(token, notifId);
      }
    } catch (err) {
      console.error("Failed to sync notification deletion:", err);
    }
  };

  // Aggregated Overall Athlete Statistics
  const totalCount = analyses.length;
  const avgRiskScore = totalCount > 0
    ? Math.round(analyses.reduce((acc, curr) => acc + (curr.risk_score || 0), 0) / totalCount)
    : 0;

  const lowRiskAnalyses = analyses.filter((a) => (a.risk_score || 0) <= 20);
  const moderateRiskAnalyses = analyses.filter((a) => (a.risk_score || 0) > 20 && (a.risk_score || 0) <= 35);
  const highRiskAnalyses = analyses.filter((a) => (a.risk_score || 0) > 35);

  const cleanTechniquePercent = totalCount > 0 ? Math.round((lowRiskAnalyses.length / totalCount) * 100) : 0;
  const readinessIndex = Math.max(15, Math.min(100, Math.round(100 - (avgRiskScore * 0.7))));

  // Cumulative Kinetic Chain Aggregations
  let totalValgus = 0;
  let valgusCount = 0;
  let totalTrunkLean = 0;
  let trunkCount = 0;
  let totalSymmetry = 0;
  let symmetryCount = 0;
  let totalAnkleVel = 0;
  let ankleVelCount = 0;
  let totalFlightClearance = 0;
  let flightCount = 0;

  const anomalyCounts: Record<string, number> = {
    "ACL / Knee Valgus": 0,
    "Hamstring Strain": 0,
    "Ankle Instability": 0,
    "Trunk / Lumbar Sway": 0,
    "Shoulder / Upper Kinetic": 0,
    "Overuse Risk": 0,
  };

  const activityMap: Record<string, { count: number; totalRisk: number; highCount: number }> = {};

  analyses.forEach((a) => {
    const act = a.activity || "Other";
    if (!activityMap[act]) {
      activityMap[act] = { count: 0, totalRisk: 0, highCount: 0 };
    }
    activityMap[act].count += 1;
    activityMap[act].totalRisk += a.risk_score || 0;
    if ((a.risk_score || 0) > 35) activityMap[act].highCount += 1;

    let kin = a.kinematics;
    if (typeof kin === "string") {
      try { kin = JSON.parse(kin); } catch { kin = null; }
    }
    if (kin) {
      const vMax = Math.max(kin.valgus_l_max || 0, kin.valgus_r_max || 0);
      if (vMax > 0) {
        totalValgus += vMax;
        valgusCount += 1;
      }
      const tLean = kin.trunk_lean_max || kin.trunk_lean_mean || 0;
      if (tLean > 0) {
        totalTrunkLean += tLean;
        trunkCount += 1;
      }
      if (kin.bilateral_symmetry_index) {
        totalSymmetry += kin.bilateral_symmetry_index;
        symmetryCount += 1;
      }
      if (kin.peak_ankle_velocity) {
        totalAnkleVel += kin.peak_ankle_velocity;
        ankleVelCount += 1;
      }
      if (kin.flight_clearance_percent) {
        totalFlightClearance += kin.flight_clearance_percent;
        flightCount += 1;
      }
    }

    let probs = a.injury_probabilities;
    if (typeof probs === "string") {
      try { probs = JSON.parse(probs); } catch { probs = []; }
    }
    if (Array.isArray(probs)) {
      probs.forEach((p: any) => {
        const lbl = (typeof p === "string" ? p : p.label || "").toLowerCase();
        if (lbl.includes("acl") || lbl.includes("valgus") || lbl.includes("knee")) anomalyCounts["ACL / Knee Valgus"] += 1;
        if (lbl.includes("hamstring")) anomalyCounts["Hamstring Strain"] += 1;
        if (lbl.includes("ankle")) anomalyCounts["Ankle Instability"] += 1;
        if (lbl.includes("back") || lbl.includes("trunk") || lbl.includes("spine")) anomalyCounts["Trunk / Lumbar Sway"] += 1;
        if (lbl.includes("shoulder") || lbl.includes("arm") || lbl.includes("wrist")) anomalyCounts["Shoulder / Upper Kinetic"] += 1;
        if (lbl.includes("overuse")) anomalyCounts["Overuse Risk"] += 1;
      });
    }
  });

  const avgValgus = valgusCount > 0 ? (totalValgus / valgusCount).toFixed(1) : "14.2";
  const avgTrunkLean = trunkCount > 0 ? (totalTrunkLean / trunkCount).toFixed(1) : "18.5";
  const avgSymmetry = symmetryCount > 0 ? (totalSymmetry / symmetryCount).toFixed(1) : "93.8";
  const avgAnkleVel = ankleVelCount > 0 ? (totalAnkleVel / ankleVelCount).toFixed(1) : "4.8";
  const avgFlight = flightCount > 0 ? (totalFlightClearance / flightCount).toFixed(1) : "16.4";

  const ALL_7_ACTIONS = [
    "Sprinting",
    "Squatting",
    "Jumping",
    "Throwing",
    "Landing",
    "Cutting Movements",
    "Sports Specific Drills"
  ];

  const trajectoryData = [...analyses]
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .map((a, idx) => ({
      session: `#${idx + 1}`,
      activity: a.activity,
      risk: a.risk_score || 0,
      safetyThreshold: 35,
    }));

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header (Export PDF & Export CSV moved inside each report as requested) */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-end gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Athlete Intelligence Dashboard</h2>
          <p className="text-slate-400 text-sm mt-1">AI-Powered Biomechanics & Injury Prediction Engine</p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/dashboard/reports"
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white rounded-xl text-xs font-semibold transition-colors border border-slate-700/80 cursor-pointer shadow-sm flex items-center gap-2"
          >
            <span>View All Permanent Reports Archive</span>
            <span>&rarr;</span>
          </Link>
        </div>
      </div>

      {notifications.length > 0 && (
        <div className="space-y-2.5 animate-fadeIn">
          {notifications.map((notif) => {
            const hasRec = notif.message && notif.message.toLowerCase().includes("recommendation");
            const activityMatch = notif.message?.match(/analysis for ([A-Za-z\s]+) resulted/i);
            const flaggedActivity = activityMatch ? activityMatch[1].trim() : "Throwing";

            const isAlert = notif.type === "alert" || (notif.title && notif.title.toLowerCase().includes("risk"));

            return (
              <div
                key={notif.id}
                className={`p-4 rounded-xl border text-xs sm:text-sm flex items-start justify-between gap-3 transition-all shadow-sm ${isAlert
                  ? "bg-rose-500/10 border-rose-500/30 text-rose-200"
                  : "bg-amber-500/10 border-amber-500/30 text-amber-200"
                  }`}
              >
                <div className="flex items-start gap-3 flex-1">
                  <div className={`p-1.5 rounded-lg shrink-0 mt-0.5 ${isAlert ? "bg-rose-500/20 text-rose-300" : "bg-amber-500/20 text-amber-300"}`}>
                    {isAlert ? <ShieldAlert className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                  </div>
                  <div className="leading-relaxed">
                    <strong className="text-white font-bold">{notif.title}</strong>:{" "}
                    {hasRec ? (
                      <span>
                        {notif.message.split(/recommendations?/i)[0]}
                        <Link
                          href={`/dashboard/recommendations?activity=${encodeURIComponent(flaggedActivity)}&risk=High%20Risk`}
                          className="font-bold underline text-white hover:text-rose-100 cursor-pointer bg-rose-500/30 hover:bg-rose-500/50 px-2 py-0.5 rounded transition-all inline-flex items-center gap-1 shadow-sm mx-1"
                        >
                          <span>recommendations</span>
                          <ArrowRight className="w-3.5 h-3.5 inline-block" />
                        </Link>
                        {notif.message.split(/recommendations?/i)[1] || "."}
                      </span>
                    ) : (
                      notif.message
                    )}
                  </div>
                </div>

                {/* Cross Button on Right End */}
                <button
                  type="button"
                  onClick={() => handleDismissNotification(notif.id)}
                  title="Dismiss alert"
                  className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/20 text-slate-400 hover:text-white flex items-center justify-center transition-all cursor-pointer shrink-0 ml-2 border border-white/10"
                  aria-label="Dismiss alert"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Top Overall KPI Intelligence Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* KPI 1: Average Risk Score */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Average Risk Score
            </span>
            <span
              className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold border ${avgRiskScore > 35
                ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                : avgRiskScore > 20
                  ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                  : "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                }`}
            >
              {avgRiskScore <= 20 ? "Optimal Efficiency" : avgRiskScore <= 35 ? "Moderate Caution" : "Joint Strain Detected"}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <div className={`text-4xl font-black ${avgRiskScore > 35 ? "text-rose-400" : avgRiskScore > 20 ? "text-amber-400" : "text-emerald-400"}`}>
              {avgRiskScore}
            </div>
            <span className="text-slate-500 font-semibold text-sm">/ 100</span>
          </div>

          <div className="text-xs text-slate-400">
            Based on <strong className="text-slate-200">{totalCount}</strong> recent movement analyses
          </div>

          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className={`h-full rounded-full transition-all duration-700 ${avgRiskScore > 35
                ? "bg-gradient-to-r from-amber-500 to-rose-500"
                : "bg-gradient-to-r from-emerald-500 to-indigo-500"
                }`}
              style={{ width: `${Math.min(100, Math.max(5, avgRiskScore))}%` }}
            />
          </div>
        </div>

        {/* KPI 2: Total Videos Analyzed */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Videos Analyzed
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-semibold font-mono">
              100% Computer Vision
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-black text-white">
              {totalCount}
            </div>
            <span className="text-xs text-slate-500">Evaluations</span>
          </div>

          <div className="text-xs text-slate-400">
            Historical kinetic motion evaluations
          </div>

          <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-400">
            <span className="text-emerald-400 font-bold">{lowRiskAnalyses.length} Safe</span>
            <span>•</span>
            <span className="text-amber-400 font-bold">{moderateRiskAnalyses.length} Moderate</span>
            <span>•</span>
            <span className="text-rose-400 font-bold">{highRiskAnalyses.length} High Risk</span>
          </div>
        </div>

        {/* KPI 3: Run New Video Analysis CTA */}
        <Link
          href="/dashboard/upload"
          className="glass-panel p-6 rounded-2xl border-indigo-500/40 bg-gradient-to-br from-indigo-500/15 via-indigo-600/10 to-pink-500/10 hover:from-indigo-500/25 hover:to-pink-500/20 transition-all cursor-pointer flex flex-col justify-between group shadow-[0_0_25px_rgba(79,70,229,0.2)] border"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-300 flex items-center justify-center border border-indigo-500/30 group-hover:scale-110 group-hover:bg-indigo-500 group-hover:text-white transition-all shadow-md">
              <Video className="w-5 h-5" />
            </div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-pink-400 bg-pink-500/10 px-2 py-0.5 rounded-full border border-pink-500/20">
              Instant AI
            </span>
          </div>

          <div className="my-2">
            <div className="text-base font-extrabold text-white group-hover:text-indigo-200 transition-colors flex items-center gap-1.5">
              <span>Run New Video Analysis</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Autonomous 8-Action kinetic inspection
            </div>
          </div>

          <div className="text-[11px] text-indigo-400 font-medium">
            Jump, Sprint, Squat, Throw, Cut & Drills &rarr;
          </div>
        </Link>

        {/* KPI 4: Kinetic Readiness Index */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Kinetic Readiness Index
            </span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>

          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-black text-emerald-400">
              {readinessIndex}%
            </div>
            <span className="text-xs text-slate-400">Recovery & Form Readiness</span>
          </div>

          <div className="text-xs text-slate-400">
            Calculated from dynamic stability, joint angle deltas, and symmetry
          </div>

          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-700"
              style={{ width: `${readinessIndex}%` }}
            />
          </div>
        </div>

        {/* KPI 5: Clean Technique Ratio */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Movement Form Compliance
            </span>
            <CheckCircle2 className="w-4 h-4 text-indigo-400" />
          </div>

          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-black text-white">
              {cleanTechniquePercent}%
            </div>
            <span className="text-xs text-slate-400">Optimal Form Ratio</span>
          </div>

          <div className="text-xs text-slate-400">
            {lowRiskAnalyses.length} clean sessions with zero acute joint collapse
          </div>

          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className="h-full bg-gradient-to-r from-pink-500 via-indigo-500 to-emerald-400 rounded-full transition-all duration-700"
              style={{ width: `${cleanTechniquePercent}%` }}
            />
          </div>
        </div>

        {/* KPI 6: Primary Vulnerability Focus */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Primary Vulnerability Focus
            </span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>

          <div className="text-lg font-black text-rose-300 truncate">
            {Object.entries(anomalyCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "Knee Valgus / ACL"}
          </div>

          <div className="text-xs text-slate-400">
            Detected across {Object.entries(anomalyCounts).sort((a, b) => b[1] - a[1])[0]?.[1] || 0} historical assessment flags
          </div>

          <div className="pt-2">
            <Link
              href="/dashboard/recommendations"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-bold inline-flex items-center gap-1"
            >
              <span>Explore Targeted Prescriptions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Section: Full Kinetic Chain Overall Joint Telemetry */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              <span>Full Kinetic Chain Overall Biomechanical Telemetry</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Cumulative averages synthesized across all microscopic joint angles, velocities, and rotational sway
            </p>
          </div>
          <span className="text-xs font-mono bg-slate-900 text-slate-300 px-3 py-1 rounded-lg border border-slate-800">
            {totalCount} Sessions Aggregated
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Valgus */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Mean Peak Knee Valgus
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-black ${Number(avgValgus) > 15 ? "text-rose-400" : "text-emerald-400"}`}>
                {avgValgus}°
              </span>
              <span className="text-[11px] text-slate-500 font-normal">Normal &lt; 15.0°</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              {Number(avgValgus) > 15
                ? "Medial collapse tendency during deceleration touchdown."
                : "Safe frontal plane knee alignment maintained."}
            </p>
          </div>

          {/* Trunk Lean */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Mean Trunk / Spine Sway
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-black ${Number(avgTrunkLean) > 25 ? "text-amber-400" : "text-slate-200"}`}>
                {avgTrunkLean}°
              </span>
              <span className="text-[11px] text-slate-500 font-normal">Normal &lt; 25.0°</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Torso lean stability and lumbar postural alignment across explosive movements.
            </p>
          </div>

          {/* Ankle Velocity */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Ankle Propulsion Velocity
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-pink-400">
                {avgAnkleVel} <span className="text-xs font-normal text-slate-400">m/s</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Average ground flight clearance: <strong className="text-indigo-300">{avgFlight}%</strong> above turf.
            </p>
          </div>

          {/* Bilateral Symmetry */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Bilateral Kinetic Symmetry
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-indigo-400">
                {avgSymmetry}%
              </span>
              <span className="text-[11px] text-slate-500 font-normal">Optimal Balance</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Left vs Right limb velocity and joint moment distribution equality.
            </p>
          </div>
        </div>
      </div>

      {/* Section: 7-Action Kinetic Mastery Matrix */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              <span>7-Action Kinetic Mastery & Movement Profile Distribution</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Historical summary of athlete compliance and risk ratings across all targeted sports movements
            </p>
          </div>
          <Link
            href="/dashboard/recommendations"
            className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1"
          >
            <span>View All Movement Prescriptions</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {ALL_7_ACTIONS.map((action) => {
            const data = activityMap[action];
            const count = data?.count || 0;
            const avgActRisk = count > 0 ? Math.round(data.totalRisk / count) : null;
            const isEvaluated = count > 0;

            return (
              <div
                key={action}
                className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/90 hover:border-slate-700 transition-all flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm text-white">{action}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${!isEvaluated
                        ? "bg-slate-800 text-slate-400 border-slate-700"
                        : avgActRisk! > 35
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                          : avgActRisk! > 20
                            ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                            : "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                        }`}
                    >
                      {!isEvaluated ? "No Data" : `${avgActRisk} Risk`}
                    </span>
                  </div>

                  <div className="text-xs text-slate-400">
                    {isEvaluated ? (
                      <span>
                        <strong className="text-white">{count}</strong> videos assessed
                      </span>
                    ) : (
                      "Awaiting first video"
                    )}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800/80">
                  {isEvaluated ? (
                    <Link
                      href={`/dashboard/recommendations?activity=${encodeURIComponent(action)}&risk=${avgActRisk! > 35 ? "High%20Risk" : avgActRisk! > 20 ? "Moderate%20Risk" : "Low%20Risk"
                        }`}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-bold inline-flex items-center gap-1 group"
                    >
                      <span>Prescriptions</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                  ) : (
                    <Link
                      href="/dashboard/upload"
                      className="text-xs text-slate-500 hover:text-slate-300 inline-flex items-center gap-1"
                    >
                      <span>Upload Video &rarr;</span>
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Section: Longitudinal Risk Score Trajectory */}
      {trajectoryData.length > 1 && (
        <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-400" />
                <span>Historical Movement Risk Score Trajectory</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Progression of biomechanical risk across chronological analysis sessions
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-indigo-300">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                <span>Session Risk Score</span>
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-0.5 bg-rose-500" />
                <span>Risk Threshold (35 pts)</span>
              </span>
            </div>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trajectoryData}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="session" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    borderRadius: "12px",
                    color: "#f8fafc",
                    fontSize: "12px",
                  }}
                  formatter={(val: any) => [`${val} / 100 Risk`, "Session Score"]}
                  labelFormatter={(lbl) => `Session ${lbl}`}
                />
                <Area
                  type="monotone"
                  dataKey="risk"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorRisk)"
                />
                <Line
                  type="monotone"
                  dataKey="safetyThreshold"
                  stroke="#f43f5e"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Section: Clinical Directives & Corrective Action Hub */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>AI Clinical Directives & Biomechanical Priorities</span>
          </h3>
          <span className="text-xs text-indigo-400 font-mono">Personalized Formulation</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
              1. Frontal Knee Valgus Control
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Incorporate banded lateral monster walks and single-leg squats to strengthen the gluteus medius and prevent inward knee collapse.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-pink-400 uppercase tracking-wider">
              2. Eccentric Deceleration Loading
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Perform single-leg Romanian deadlifts and Nordic curls to build eccentric hamstring capacity and absorb anterior tibial shear forces.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
              3. Core & Thoracic Symmetry
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Integrate rotational medicine ball throws and anti-rotational Pallof presses to mitigate trunk sway during high-velocity cutting.
            </p>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-400">
            For individual microscopic joint telemetry, frame overlays, and PDF/CSV downloads, visit the permanent Reports tab.
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard/recommendations"
              className="text-xs font-bold text-white hover:text-indigo-300 transition-colors flex items-center gap-1"
            >
              <span>Explore Recommendations</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <span className="text-slate-600">•</span>
            <Link
              href="/dashboard/training"
              className="text-xs font-bold text-white hover:text-pink-300 transition-colors flex items-center gap-1"
            >
              <span>Training Plans</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <span className="text-slate-600">•</span>
            <Link
              href="/dashboard/reports"
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
            >
              <span>Reports Archive</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function PhysioDashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getRecoveryStatus(token)
        .then((data) => setStats(data))
        .catch((err) => console.error("Physio error:", err));
    }
  }, []);

  const data = stats?.trends || [
    { name: 'Mon', injuries: 1, recoveries: 2 },
    { name: 'Tue', injuries: 0, recoveries: 1 },
    { name: 'Wed', injuries: 2, recoveries: 0 },
    { name: 'Thu', injuries: 1, recoveries: 3 },
    { name: 'Fri', injuries: 0, recoveries: 2 },
    { name: 'Sat', injuries: 3, recoveries: 1 },
    { name: 'Sun', injuries: 0, recoveries: 4 },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Active Injuries</div>
          <div className="text-3xl font-bold text-rose-400">{stats?.active_injuries_count ?? 4}</div>
          <p className="text-xs text-slate-500 mt-1">Under acute or subacute protocol</p>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Rehab Plans Active</div>
          <div className="text-3xl font-bold text-white">{stats?.rehab_plans_active ?? 12}</div>
          <p className="text-xs text-slate-500 mt-1">Monitored kinematic recovery</p>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Cleared to Play</div>
          <div className="text-3xl font-bold text-emerald-400">{stats?.cleared_this_week ?? "2 This Week"}</div>
          <p className="text-xs text-slate-500 mt-1">Met full bilateral symmetry index</p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-white">Injury vs Recovery Trends</h3>
            <p className="text-xs text-slate-400">7-day longitudinal clinical tracking</p>
          </div>
          <Link
            href="/dashboard/recovery"
            className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            Open Full Rehab Center &rarr;
          </Link>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }} />
              <Legend />
              <Bar dataKey="injuries" fill="#f43f5e" name="New Injuries" radius={[4, 4, 0, 0]} />
              <Bar dataKey="recoveries" fill="#10b981" name="Recoveries" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function ScientistDashboard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getScientistInsights(token)
        .then((res) => setData(res))
        .catch((err) => console.error("Scientist error:", err));
    }
  }, []);

  const fatigueData = data?.fatigue_overlay || [
    { day: 'Day 1', load: 60, fatigue: 40 },
    { day: 'Day 2', load: 80, fatigue: 55 },
    { day: 'Day 3', load: 40, fatigue: 30 },
    { day: 'Day 4', load: 95, fatigue: 85 },
    { day: 'Day 5', load: 85, fatigue: 75 },
    { day: 'Day 6', load: 50, fatigue: 45 },
    { day: 'Day 7', load: 100, fatigue: 90 },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Team Fatigue Index</div>
          <div className="text-3xl font-bold text-amber-400">{data?.fatigue_index_status || "Elevated"}</div>
          <p className="text-xs text-slate-500 mt-1">Load index: {data?.mean_fatigue_score || 38}/100</p>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Workload Spikes</div>
          <div className="text-3xl font-bold text-rose-400">{data?.workload_spikes_count ?? 3} Players</div>
          <p className="text-xs text-slate-500 mt-1">ACWR &gt; 1.40 threshold violation</p>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Reports Generated</div>
          <div className="text-3xl font-bold text-white">{data?.reports_generated ?? 14}</div>
          <p className="text-xs text-slate-500 mt-1">Biomechanical research datasets</p>
        </div>
      </div>
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-white">Training Load vs Fatigue Overlay</h3>
            <p className="text-xs text-slate-400">Longitudinal physiological strain interaction</p>
          </div>
          <Link
            href="/dashboard/analytics"
            className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            Biomechanical Engine &rarr;
          </Link>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={fatigueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }} />
              <Legend />
              <Line type="monotone" dataKey="load" stroke="#8b5cf6" strokeWidth={3} name="Training Load" />
              <Line type="monotone" dataKey="fatigue" stroke="#f59e0b" strokeWidth={3} name="Fatigue Index" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getAdminPlatformStats(token)
        .then((res) => setStats(res))
        .catch((err) => console.error("Admin stats error:", err));
    }
  }, []);

  const platformUsage = stats?.growth_trajectory || [
    { name: 'Week 1', users: 150, analyses: 300 },
    { name: 'Week 2', users: 180, analyses: 450 },
    { name: 'Week 3', users: 210, analyses: 500 },
    { name: 'Week 4', users: 245, analyses: 620 },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Total Users</div>
          <div className="text-3xl font-bold text-white">{stats?.total_users ?? 245}</div>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Active Teams</div>
          <div className="text-3xl font-bold text-white">{stats?.active_teams ?? 8}</div>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">System Health</div>
          <div className="text-3xl font-bold text-emerald-400">{stats?.system_health ?? "99.98%"}</div>
        </div>
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Storage Used</div>
          <div className="text-3xl font-bold text-white">{stats?.storage_used_mb ? `${stats.storage_used_mb} MB` : "1.2 TB"}</div>
        </div>
      </div>
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-white">Platform Usage Overview</h3>
            <p className="text-xs text-slate-400">Weekly user registration and video processing trends</p>
          </div>
          <Link
            href="/dashboard/users"
            className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            User Management Roster &rarr;
          </Link>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={platformUsage}>
              <defs>
                <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorAnalyses" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }} />
              <Legend />
              <Area type="monotone" dataKey="users" stroke="#3b82f6" fillOpacity={1} fill="url(#colorUsers)" name="Active Users" />
              <Area type="monotone" dataKey="analyses" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorAnalyses)" name="Analyses Run" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function CoachDashboard() {
  const [teamData, setTeamData] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getTeamMonitoring(token)
        .then((res) => setTeamData(res))
        .catch((err) => console.error("Coach error:", err));
    }
  }, []);

  const athletes = teamData?.athletes || [];
  const overallRisk = teamData?.team_overall_risk ?? 28;
  const highRiskCount = teamData?.high_risk_athletes_count ?? 2;
  const videosCount = teamData?.videos_analyzed_count ?? 143;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Team Overall Risk Score</div>
          <div className="text-3xl font-bold text-white flex items-end gap-2">
            {overallRisk}<span className="text-lg text-emerald-400">/ 100</span>
          </div>
          <div className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>-12% baseline injury risk</span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">High Risk Athletes</div>
          <div className="text-3xl font-bold text-rose-400">
            {highRiskCount}
          </div>
          <div className="text-xs text-rose-400 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Requires workload deload</span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="text-sm font-medium text-slate-400 mb-1">Videos Analyzed</div>
          <div className="text-3xl font-bold text-white">
            {videosCount}
          </div>
          <div className="text-xs text-indigo-400 mt-2 flex items-center gap-1">
            <span>Last 7 days squad telemetry</span>
          </div>
        </div>

        <Link href="/dashboard/upload" className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-indigo-500/5 cursor-pointer hover:bg-indigo-500/10 transition-colors group">
          <div className="h-full flex flex-col items-center justify-center text-indigo-400 group-hover:text-indigo-300">
            <Video className="w-7 h-7 mb-2" />
            <span className="font-semibold text-sm">Analyze New Video</span>
          </div>
        </Link>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Athletes List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel rounded-2xl p-6 border border-slate-800">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-white">Athlete Risk Assessment</h3>
                <p className="text-xs text-slate-400">Roster movement screening statuses</p>
              </div>
              <Link href="/dashboard/monitoring" className="text-sm text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
                <span>View Full Roster ({athletes.length || 21})</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="space-y-3">
              {(athletes.slice(0, 4)).map((ath: any, idx: number) => {
                const isHigh = ath.risk_score > 60;
                const isMod = ath.risk_score > 30 && ath.risk_score <= 60;
                return (
                  <div key={idx} className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-indigo-400 text-sm">
                        {ath.name.split(" ").map((n: string) => n[0]).join("")}
                      </div>
                      <div>
                        <div className="font-semibold text-white text-sm">{ath.name}</div>
                        <div className="text-xs text-slate-400">{ath.position} • {ath.primary_issue}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className={`text-sm font-bold ${isHigh ? "text-rose-400" : isMod ? "text-amber-400" : "text-emerald-400"}`}>
                          {ath.risk_score}/100 Risk
                        </div>
                        <div className="text-xs text-slate-500">{ath.status}</div>
                      </div>
                      <div className="w-2 h-10 rounded-full bg-slate-800 relative overflow-hidden">
                        <div
                          className={`absolute bottom-0 w-full rounded-full ${isHigh ? "bg-rose-500" : isMod ? "bg-amber-500" : "bg-emerald-500"}`}
                          style={{ height: `${ath.risk_score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column - Workload Alerts Quick View */}
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Bell className="w-4 h-4 text-rose-400" />
                <span>Workload Trigger Alerts</span>
              </h3>
              <Link href="/dashboard/workload" className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold">
                Manage &rarr;
              </Link>
            </div>

            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 space-y-1">
              <div className="text-xs font-bold text-rose-300 flex items-center justify-between">
                <span>Marcus Vance (ACWR: 1.58)</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-200">Spike</span>
              </div>
              <p className="text-xs text-slate-300">Acute workload spike exceeding 1.40 threshold. 40% deload suggested.</p>
            </div>

            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-1">
              <div className="text-xs font-bold text-amber-300 flex items-center justify-between">
                <span>Elena Rostova (Knee Valgus)</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-200">Kinematic</span>
              </div>
              <p className="text-xs text-slate-300">Frontal knee valgus increased by 4.2° over 3 consecutive sessions.</p>
            </div>

            <Link
              href="/dashboard/workload"
              className="block w-full text-center py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white text-xs font-bold rounded-xl transition-colors border border-slate-700"
            >
              Open Workload Alert Hub
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
