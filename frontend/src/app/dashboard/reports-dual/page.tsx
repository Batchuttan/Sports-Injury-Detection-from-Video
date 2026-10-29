"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import {
  getDualComparisons,
  getSingleDualComparison,
  deleteDualComparisons,
  downloadDualComparisonPdf,
  downloadDualComparisonCsv,
  API_URL
} from "@/lib/api";
import {
  FileText,
  Trash2,
  CheckSquare,
  Square,
  Search,
  Filter,
  Download,
  Eye,
  AlertTriangle,
  Sparkles,
  Compass,
  CheckCircle2,
  X,
  XCircle,
  Activity,
  ArrowRight,
  ShieldCheck,
  GitBranch,
  ArrowUpCircle,
  ArrowDownCircle,
  Footprints,
  Zap,
  Target,
  Film,
  Play,
  Pause,
  RotateCcw,
  Volume2,
  VolumeX,
  PlayCircle
} from "lucide-react";

const resolveVideoSrc = (raw?: string | null) => {
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
  let path = raw.startsWith("/") ? raw : `/${raw}`;
  if (!path.startsWith("/processed/") && !path.startsWith("/uploads/")) {
    path = `/processed/${path.replace(/^\/+/, "")}`;
  }
  return `${API_URL}${path}`;
};

const ACTION_ICONS: Record<string, React.ReactNode> = {
  "Jumping": <ArrowUpCircle className="w-4 h-4 text-sky-400" />,
  "Squatting": <ArrowDownCircle className="w-4 h-4 text-indigo-400" />,
  "Sprinting": <Zap className="w-4 h-4 text-amber-400" />,
  "Landing": <ShieldCheck className="w-4 h-4 text-teal-400" />,
  "Throwing": <Target className="w-4 h-4 text-rose-400" />,
  "Cutting Movements": <GitBranch className="w-4 h-4 text-violet-400" />,
  "Sports Specific Drills": <Activity className="w-4 h-4 text-orange-400" />
};

export default function DualReportsArchivePage() {
  const [comparisons, setComparisons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterVerdict, setFilterVerdict] = useState<string>("All");

  // Selection & Delete Mode
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [deleting, setDeleting] = useState(false);
  const [deleteMessage, setDeleteMessage] = useState("");

  // Modal State
  const [selectedComp, setSelectedComp] = useState<any | null>(null);
  const [loadingModalId, setLoadingModalId] = useState<number | null>(null);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingCsv, setExportingCsv] = useState(false);

  // Synchronized Dual Video Playback State
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPlayingA, setIsPlayingA] = useState(true);
  const [isPlayingB, setIsPlayingB] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const videoRefA = useRef<HTMLVideoElement | null>(null);
  const videoRefB = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    if (selectedComp) {
      setIsPlaying(true);
      setIsPlayingA(true);
      setIsPlayingB(true);
      setTimeout(() => {
        if (videoRefA.current) videoRefA.current.play().catch(() => { });
        if (videoRefB.current) videoRefB.current.play().catch(() => { });
      }, 300);
    } else {
      setIsPlaying(false);
    }
  }, [selectedComp]);

  const togglePlayBoth = () => {
    const vA = videoRefA.current;
    const vB = videoRefB.current;
    if (!vA && !vB) return;

    if (isPlaying) {
      if (vA) vA.pause();
      if (vB) vB.pause();
      setIsPlaying(false);
      setIsPlayingA(false);
      setIsPlayingB(false);
    } else {
      if (vA) vA.play().catch(() => { });
      if (vB) vB.play().catch(() => { });
      setIsPlaying(true);
      setIsPlayingA(true);
      setIsPlayingB(true);
    }
  };

  const restartBoth = () => {
    const vA = videoRefA.current;
    const vB = videoRefB.current;
    if (vA) {
      vA.currentTime = 0;
      vA.play().catch(() => { });
    }
    if (vB) {
      vB.currentTime = 0;
      vB.play().catch(() => { });
    }
    setIsPlaying(true);
    setIsPlayingA(true);
    setIsPlayingB(true);
  };

  const toggleMuteBoth = () => {
    const nextMuted = !isMuted;
    setIsMuted(nextMuted);
    if (videoRefA.current) videoRefA.current.muted = nextMuted;
    if (videoRefB.current) videoRefB.current.muted = nextMuted;
  };

  const changeSpeed = (speed: number) => {
    setPlaybackSpeed(speed);
    if (videoRefA.current) videoRefA.current.playbackRate = speed;
    if (videoRefB.current) videoRefB.current.playbackRate = speed;
  };

  const playSingleVideo = (which: "A" | "B") => {
    const target = which === "A" ? videoRefA.current : videoRefB.current;
    if (!target) return;
    if (target.paused) {
      target.play().catch(() => { });
      if (which === "A") setIsPlayingA(true);
      else setIsPlayingB(true);
    } else {
      target.pause();
      if (which === "A") setIsPlayingA(false);
      else setIsPlayingB(false);
    }
  };

  const fetchDualReports = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const data = await getDualComparisons(token);
      setComparisons(data || []);
    } catch (err) {
      console.error("Failed to load dual comparisons:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDualReports();
  }, []);

  const handleViewComparison = async (compSummary: any) => {
    setLoadingModalId(compSummary.id);
    try {
      const token = localStorage.getItem("token");
      if (token) {
        const full = await getSingleDualComparison(token, compSummary.id);
        setSelectedComp(full);
      } else {
        setSelectedComp(compSummary);
      }
    } catch (err) {
      console.warn("Falling back to local comp data:", err);
      setSelectedComp(compSummary);
    } finally {
      setLoadingModalId(null);
    }
  };

  const handleExportPdf = async (comp: any) => {
    try {
      setExportingPdf(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const safeTitle = `${comp.video_a_activity || 'V1'}_vs_${comp.video_b_activity || 'V2'}`.replace(/\s+/g, "_");
      await downloadDualComparisonPdf(token, comp.id, `SportsAI_Dual_Report_${comp.id}_${safeTitle}.pdf`);
    } catch (err: any) {
      alert("Failed to export PDF: " + err.message);
    } finally {
      setExportingPdf(false);
    }
  };

  const handleExportCsv = async (comp: any) => {
    try {
      setExportingCsv(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const safeTitle = `${comp.video_a_activity || 'V1'}_vs_${comp.video_b_activity || 'V2'}`.replace(/\s+/g, "_");
      await downloadDualComparisonCsv(token, comp.id, `SportsAI_Dual_Report_${comp.id}_${safeTitle}.xlsx`);
    } catch (err: any) {
      alert("Failed to export CSV: " + err.message);
    } finally {
      setExportingCsv(false);
    }
  };

  const toggleSelectComp = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIds.size === filteredComparisons.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredComparisons.map((c) => c.id)));
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) return;
    const confirmDelete = window.confirm(
      `Are you sure you want to permanently delete ${selectedIds.size} selected dual comparison report(s)? This action cannot be undone.`
    );
    if (!confirmDelete) return;

    try {
      setDeleting(true);
      const token = localStorage.getItem("token");
      if (!token) return;

      const idsArray = Array.from(selectedIds);
      const res = await deleteDualComparisons(token, idsArray);
      setDeleteMessage(res.message || `Deleted ${idsArray.length} dual reports successfully.`);
      setSelectedIds(new Set());
      setIsDeleteMode(false);
      await fetchDualReports();
      setTimeout(() => setDeleteMessage(""), 4000);
    } catch (err: any) {
      alert("Failed to delete dual comparison reports: " + err.message);
    } finally {
      setDeleting(false);
    }
  };

  const filteredComparisons = comparisons.filter((c) => {
    const actA = (c.video_a_activity || "").toLowerCase();
    const actB = (c.video_b_activity || "").toLowerCase();
    const verdict = (c.overall_verdict || "").toLowerCase();
    const summary = (c.summary || "").toLowerCase();
    const search = searchTerm.toLowerCase();

    const matchesSearch =
      actA.includes(search) ||
      actB.includes(search) ||
      verdict.includes(search) ||
      summary.includes(search) ||
      String(c.id).includes(search);

    let matchesFilter = true;
    if (filterVerdict === "Improvements") {
      matchesFilter = (c.score_diff < 0) || verdict.includes("improvement") || verdict.includes("positive");
    } else if (filterVerdict === "Regressions") {
      matchesFilter = (c.score_diff > 0) || verdict.includes("regression") || verdict.includes("risk");
    } else if (filterVerdict === "Neutral") {
      matchesFilter = (c.score_diff === 0) || verdict.includes("neutral") || verdict.includes("baseline");
    }

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-24 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <Link href="/dashboard" className="hover:text-indigo-400 transition-colors">
              Dashboard
            </Link>
            <span>•</span>
            <span className="text-pink-400 font-medium">Dual Video Reports Archive</span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <GitBranch className="w-7 h-7 text-pink-400 shrink-0" />
            <span>Dual Video Biomechanics & Comparison Reports Archive</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Permanent record of all comparative dual video evaluations, 8-action kinetic matrices, joint telemetry deltas, and progression reports.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/compare"
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(236,72,153,0.3)] shrink-0 flex items-center gap-1.5"
          >
            <GitBranch className="w-4 h-4" />
            <span>Compare 2 Videos</span>
          </Link>
        </div>
      </div>

      {deleteMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{deleteMessage}</span>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search activities, verdict, ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900/80 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-pink-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
          <div className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400 ml-2" />
            {[
              { id: "All", label: "All Comparisons" },
              { id: "Improvements", label: "Improvements" },
              { id: "Regressions", label: "Regressions" },
              { id: "Neutral", label: "Stable Baselines" }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilterVerdict(tab.id)}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors cursor-pointer ${filterVerdict === tab.id ? "bg-pink-600 text-white" : "text-slate-400 hover:text-white"
                  }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <span className="text-xs text-slate-500 font-mono bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800 shrink-0">
            {filteredComparisons.length} Dual Reports
          </span>
        </div>
      </div>

      {/* Dual Reports Grid */}
      {loading ? (
        <div className="glass-panel p-20 rounded-3xl border border-slate-800 text-center flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 border-2 border-pink-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-slate-400">Loading dual video comparison archive...</span>
        </div>
      ) : filteredComparisons.length === 0 ? (
        <div className="glass-panel p-16 rounded-3xl border border-slate-800 text-center space-y-3">
          <GitBranch className="w-10 h-10 text-slate-600 mx-auto" />
          <h4 className="text-base font-bold text-white">No dual video reports found</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            You have not recorded any dual video comparisons matching this criteria yet. Upload or select two sessions to compare.
          </p>
          <div className="pt-2">
            <Link
              href="/dashboard/compare"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-pink-600 hover:bg-pink-500 text-white text-xs font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(236,72,153,0.3)]"
            >
              <GitBranch className="w-4 h-4" />
              <span>Launch Video Comparison</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredComparisons.map((comp) => {
            const isSelected = selectedIds.has(comp.id);
            const scoreDiff = comp.score_diff ?? (comp.video_b_risk_score - comp.video_a_risk_score);
            const isImprovement = scoreDiff < 0;
            const isRegression = scoreDiff > 0;

            return (
              <div
                key={comp.id}
                onClick={() => isDeleteMode && toggleSelectComp(comp.id)}
                className={`bg-slate-900/60 p-5 rounded-2xl border transition-all flex flex-col justify-between space-y-4 relative group ${isSelected
                  ? "border-rose-500/80 bg-rose-950/20 shadow-[0_0_20px_rgba(244,63,94,0.2)]"
                  : "border-slate-800 hover:border-slate-700"
                  } ${isDeleteMode ? "cursor-pointer" : ""}`}
              >
                {/* Delete Checkbox in Selection Mode */}
                {isDeleteMode && (
                  <div className="absolute top-4 right-4 z-10">
                    {isSelected ? (
                      <CheckSquare className="w-5 h-5 text-rose-400 fill-rose-500/20" />
                    ) : (
                      <Square className="w-5 h-5 text-slate-500 hover:text-slate-300" />
                    )}
                  </div>
                )}

                {/* Card Top Information */}
                <div className="space-y-3">
                  <div className="flex justify-between items-start gap-2 pr-6">
                    <div>
                      <div className="text-white font-bold text-base flex items-center gap-2 flex-wrap">
                        <span className="text-indigo-400">{comp.video_a_activity}</span>
                        <span className="text-slate-500 text-xs">vs</span>
                        <span className="text-pink-400">{comp.video_b_activity}</span>
                        <span className="text-[10px] text-slate-500 font-mono">#{comp.id}</span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {comp.created_at ? new Date(comp.created_at).toLocaleDateString() : "Historical Record"} •{" "}
                        {comp.created_at ? new Date(comp.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Archived"}
                      </div>
                    </div>

                    <div
                      className={`px-2.5 py-1 rounded-xl text-xs font-extrabold shrink-0 border ${isImprovement
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        : isRegression
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                          : "bg-slate-700/40 text-slate-300 border-slate-600/40"
                        }`}
                    >
                      {scoreDiff > 0 ? "+" : ""}{scoreDiff} pts
                    </div>
                  </div>

                  {/* Side-by-Side Risk Score Badges */}
                  <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                    <div>
                      <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-bold block mb-0.5">
                        Video 1 (Baseline)
                      </span>
                      <div className="text-lg font-black text-white">
                        {comp.video_a_risk_score}
                        <span className="text-xs text-slate-500 font-normal"> / 100 Risk</span>
                      </div>
                    </div>

                    <div className="border-l border-slate-800/80 pl-2">
                      <span className="text-[10px] uppercase tracking-wider text-pink-400 font-bold block mb-0.5">
                        Video 2 (Trial)
                      </span>
                      <div className="text-lg font-black text-white">
                        {comp.video_b_risk_score}
                        <span className="text-xs text-slate-500 font-normal"> / 100 Risk</span>
                      </div>
                    </div>
                  </div>

                  {/* Overall Verdict Badge & Footage Indicator */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider border ${comp.verdict_color === "emerald" || isImprovement
                        ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                        : comp.verdict_color === "rose" || isRegression
                          ? "bg-rose-500/15 text-rose-400 border-rose-500/30"
                          : "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        }`}
                    >
                      {comp.overall_verdict || (isImprovement ? "Kinetic Improvement" : isRegression ? "Elevated Fatigue" : "Stable Baseline")}
                    </span>

                    {(comp.video_a_url || comp.video_a_filename || comp.video_b_url || comp.video_b_filename) && (
                      <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 font-semibold">
                        <Film className="w-3 h-3 text-indigo-400" />
                        Dual Footage
                      </span>
                    )}
                  </div>

                  {/* Summary Snippet */}
                  <div className="text-xs text-slate-300 bg-slate-900/90 p-3 rounded-xl border border-slate-800 line-clamp-2 leading-relaxed">
                    {comp.summary || "Comparative kinematics calculated between Video 1 and Video 2 recordings."}
                  </div>
                </div>

                {/* Card Action Button: Prominent VIEW Button */}
                <div className="pt-3 border-t border-slate-800/80">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewComparison(comp);
                    }}
                    disabled={loadingModalId === comp.id}
                    className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-bold text-xs rounded-xl shadow-[0_0_15px_rgba(236,72,153,0.3)] transition-all flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <Eye className="w-4 h-4 shrink-0" />
                    <span>{loadingModalId === comp.id ? "Loading Telemetry..." : "VIEW FULL COMPARISON & TELEMETRY"}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Bottom Sticky Action Bar: Delete Reports Option on the End Left */}
      <div className="fixed bottom-0 left-0 right-0 z-40 bg-slate-950/90 backdrop-blur-md border-t border-slate-800 p-4 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Left Corner: Delete Reports Button */}
          <div className="flex items-center gap-3 w-full sm:w-auto">
            {!isDeleteMode ? (
              <button
                type="button"
                onClick={() => setIsDeleteMode(true)}
                className="px-4 py-2 bg-rose-950/30 hover:bg-rose-900/40 text-rose-300 border border-rose-500/40 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer"
              >
                <Trash2 className="w-4 h-4 text-rose-400" />
                <span>Delete Reports</span>
              </button>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={selectAll}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 flex items-center gap-1.5 cursor-pointer"
                >
                  <CheckSquare className="w-3.5 h-3.5 text-pink-400" />
                  <span>{selectedIds.size === filteredComparisons.length ? "Deselect All" : "Select All"}</span>
                </button>

                <button
                  type="button"
                  onClick={handleDeleteSelected}
                  disabled={selectedIds.size === 0 || deleting}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-[0_0_15px_rgba(244,63,94,0.4)] flex items-center gap-2 cursor-pointer transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>{deleting ? "Deleting..." : `Confirm Delete (${selectedIds.size} Selected)`}</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setIsDeleteMode(false);
                    setSelectedIds(new Set());
                  }}
                  className="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-400 rounded-xl text-xs font-medium border border-slate-800 cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            )}

            <div className="text-xs text-slate-400 hidden sm:block">
              {isDeleteMode ? "Select reports to delete permanently." : "Delete unwanted historical video records."}
            </div>
          </div>

          {/* Right Corner: Quick Links */}
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Viewing permanent archive</span>
            <span>•</span>
            <Link href="/dashboard" className="text-indigo-400 hover:underline">
              Back to Home
            </Link>
          </div>
        </div>
      </div>

      {/* EXPANDABLE FULL COMPARISON MODAL */}
      {selectedComp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto animate-fadeIn">
          <div className="bg-slate-900 border border-slate-700/80 rounded-3xl max-w-5xl w-full max-h-[92vh] overflow-y-auto shadow-2xl p-6 sm:p-8 space-y-6 text-slate-200">
            {/* Modal Top Header with PDF/CSV options & close button */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                  <span className="font-mono text-pink-400 font-bold">Dual Assessment #{selectedComp.id}</span>
                  <span>•</span>
                  <span>{selectedComp.created_at ? new Date(selectedComp.created_at).toLocaleDateString() : "Historical Assessment"}</span>
                </div>
                <h3 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2.5">
                  <span className="text-indigo-400">{selectedComp.video_a_activity}</span>
                  <span className="text-slate-500 text-sm font-semibold">vs</span>
                  <span className="text-pink-400">{selectedComp.video_b_activity}</span>
                </h3>
              </div>

              {/* In-Modal PDF and CSV Export Buttons + Close Button */}
              <div className="flex items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => handleExportPdf(selectedComp)}
                  disabled={exportingPdf}
                  className="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-slate-950 hover:to-slate-950 hover:bg-slate-950 text-white hover:text-purple-200 rounded-xl text-xs font-bold transition-all shadow-[0_0_16px_rgba(168,85,247,0.45)] hover:shadow-[0_0_14px_rgba(147,51,234,0.35)] border border-purple-400/40 hover:border-purple-500 flex items-center gap-1.5 cursor-pointer disabled:opacity-50 group"
                  title="Export full dual video comparison report as PDF"
                >
                  <Download className="w-3.5 h-3.5 text-white group-hover:text-purple-300 transition-colors" />
                  <span>{exportingPdf ? "Generating..." : "Export PDF"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleExportCsv(selectedComp)}
                  disabled={exportingCsv}
                  className="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-slate-950 hover:to-slate-950 hover:bg-slate-950 text-white hover:text-purple-200 rounded-xl text-xs font-bold transition-all shadow-[0_0_16px_rgba(168,85,247,0.45)] hover:shadow-[0_0_14px_rgba(147,51,234,0.35)] border border-purple-400/40 hover:border-purple-500 flex items-center gap-1.5 cursor-pointer disabled:opacity-50 group"
                  title="Export raw telemetry and matrix with customized column widths"
                >
                  <Download className="w-3.5 h-3.5 text-white group-hover:text-purple-300 transition-colors" />
                  <span>{exportingCsv ? "Exporting..." : "Export CSV"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedComp(null)}
                  className="p-2 text-slate-400 hover:text-white rounded-xl bg-slate-800/80 hover:bg-slate-700 transition-colors cursor-pointer ml-1"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Executive Verdict Banner */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden bg-slate-950/60">
              <div
                className={`absolute top-0 left-0 w-2 h-full ${selectedComp.score_diff < 0
                  ? "bg-emerald-500"
                  : selectedComp.score_diff > 0
                    ? "bg-rose-500"
                    : "bg-amber-500"
                  }`}
              />
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pl-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${selectedComp.score_diff < 0
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : selectedComp.score_diff > 0
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        }`}
                    >
                      {selectedComp.overall_verdict || "Comparative Telemetry"}
                    </span>
                    <span className="text-xs text-slate-400">
                      Net Score Delta:{" "}
                      <strong className={selectedComp.score_diff < 0 ? "text-emerald-400" : selectedComp.score_diff > 0 ? "text-rose-400" : "text-slate-200"}>
                        {selectedComp.score_diff > 0 ? "+" : ""}{selectedComp.score_diff} pts
                      </strong>
                    </span>
                  </div>
                  <h4 className="text-base font-bold text-white">
                    {selectedComp.summary}
                  </h4>
                </div>

                <div className="flex items-center gap-4 shrink-0 bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                  <div className="text-right">
                    <div className="text-[10px] text-indigo-400 font-bold uppercase">Video 1</div>
                    <div className="text-xl font-black text-white">{selectedComp.video_a_risk_score}/100</div>
                  </div>
                  <div className="text-slate-500 text-lg">&rarr;</div>
                  <div className="text-left">
                    <div className="text-[10px] text-pink-400 font-bold uppercase">Video 2</div>
                    <div className="text-xl font-black text-white">{selectedComp.video_b_risk_score}/100</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Synchronized Dual Video Players */}
            {(() => {
              const urlA = resolveVideoSrc(selectedComp.video_a_url || selectedComp.video_a_filename);
              const urlB = resolveVideoSrc(selectedComp.video_b_url || selectedComp.video_b_filename);

              if (!urlA && !urlB) return null;

              return (
                <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 bg-slate-950/70 shadow-inner">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <PlayCircle className="w-5 h-5 text-indigo-400" />
                      <h4 className="text-sm sm:text-base font-bold text-white">Synchronized Movement Comparison Playback</h4>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold rounded-md">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        Low-Latency Hardware Accelerated (GMeet Ready)
                      </span>
                    </div>

                    {/* Master Playback Controls */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <button
                        type="button"
                        onClick={togglePlayBoth}
                        className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all flex items-center gap-1.5 cursor-pointer shadow-[0_0_15px_rgba(99,102,241,0.35)]"
                      >
                        {isPlaying ? (
                          <>
                            <Pause className="w-3.5 h-3.5" />
                            <span>Pause Both</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-3.5 h-3.5 fill-white" />
                            <span>Resume Both</span>
                          </>
                        )}
                      </button>
                      <button
                        type="button"
                        onClick={restartBoth}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition-colors flex items-center gap-1 cursor-pointer"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Restart</span>
                      </button>
                      <button
                        type="button"
                        onClick={toggleMuteBoth}
                        className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors flex items-center gap-1 cursor-pointer ${isMuted
                          ? "bg-slate-800 text-slate-300 border-slate-700 hover:text-white"
                          : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          }`}
                      >
                        {isMuted ? <VolumeX className="w-3.5 h-3.5 text-slate-400" /> : <Volume2 className="w-3.5 h-3.5 text-emerald-400" />}
                        <span>{isMuted ? "Muted" : "Audio On"}</span>
                      </button>
                      <div className="flex bg-slate-900 rounded-xl p-0.5 border border-slate-800">
                        {[0.5, 1, 1.5].map((spd) => (
                          <button
                            type="button"
                            key={spd}
                            onClick={() => changeSpeed(spd)}
                            className={`px-2 py-1 text-xs rounded-lg font-medium transition-colors cursor-pointer ${playbackSpeed === spd ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                              }`}
                          >
                            {spd}x
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Side-by-side Players */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Video A */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs px-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-indigo-400">
                            Video 1: {selectedComp.video_a_activity || selectedComp.video_a_filename || "Baseline Video"}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => playSingleVideo("A")}
                            className="px-2 py-0.5 rounded bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 text-[10px] font-bold cursor-pointer"
                          >
                            {isPlayingA ? "Pause" : "Resume"}
                          </button>
                          {urlA && (
                            <a
                              href={urlA}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] text-slate-400 hover:text-indigo-300 transition-colors"
                            >
                              Open Raw ↗
                            </a>
                          )}
                        </div>
                      </div>
                      <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative group flex items-center justify-center">
                        {urlA ? (
                          <video
                            ref={videoRefA}
                            src={urlA}
                            controls
                            autoPlay
                            loop
                            playsInline
                            preload="auto"
                            muted={isMuted}
                            crossOrigin="anonymous"
                            disablePictureInPicture
                            onPlay={() => {
                              setIsPlaying(true);
                              setIsPlayingA(true);
                            }}
                            onPause={() => {
                              setIsPlayingA(false);
                              if (!videoRefB.current || videoRefB.current.paused) {
                                setIsPlaying(false);
                              }
                            }}
                            className="w-full h-full object-contain transform-gpu"
                            style={{ transform: "translateZ(0)", willChange: "transform", backfaceVisibility: "hidden" }}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs">
                            Processed video not stored for historical record
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Video B */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs px-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-pink-400">
                            Video 2: {selectedComp.video_b_activity || selectedComp.video_b_filename || "Trial Video"}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => playSingleVideo("B")}
                            className="px-2 py-0.5 rounded bg-pink-600/30 hover:bg-pink-600/50 text-pink-200 border border-pink-500/40 text-[10px] font-bold cursor-pointer"
                          >
                            {isPlayingB ? "Pause" : "Resume"}
                          </button>
                          {urlB && (
                            <a
                              href={urlB}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] text-slate-400 hover:text-pink-300 transition-colors"
                            >
                              Open Raw ↗
                            </a>
                          )}
                        </div>
                      </div>
                      <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative group flex items-center justify-center">
                        {urlB ? (
                          <video
                            ref={videoRefB}
                            src={urlB}
                            controls
                            autoPlay
                            loop
                            playsInline
                            preload="auto"
                            muted={isMuted}
                            crossOrigin="anonymous"
                            disablePictureInPicture
                            onPlay={() => {
                              setIsPlaying(true);
                              setIsPlayingB(true);
                            }}
                            onPause={() => {
                              setIsPlayingB(false);
                              if (!videoRefA.current || videoRefA.current.paused) {
                                setIsPlaying(false);
                              }
                            }}
                            className="w-full h-full object-contain transform-gpu"
                            style={{ transform: "translateZ(0)", willChange: "transform", backfaceVisibility: "hidden" }}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs">
                            Processed video not stored for historical record
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* 4-Stat High Level Kinematic Diffs */}
            {selectedComp.metrics_diff && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {/* Risk Score */}
                <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Overall Risk Score</div>
                  <div className="text-lg font-black text-white mt-1">
                    {selectedComp.metrics_diff.risk_score?.video_a} &rarr; {selectedComp.metrics_diff.risk_score?.video_b}
                  </div>
                  <div className={`text-[11px] font-bold mt-0.5 ${(selectedComp.metrics_diff.risk_score?.diff || 0) < 0 ? "text-emerald-400" : "text-rose-400"
                    }`}>
                    {(selectedComp.metrics_diff.risk_score?.diff || 0) > 0 ? "+" : ""}
                    {selectedComp.metrics_diff.risk_score?.diff} pts
                  </div>
                </div>

                {/* Max Knee Valgus */}
                <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Max Knee Valgus</div>
                  <div className="text-lg font-black text-white mt-1">
                    {selectedComp.metrics_diff.knee_valgus?.video_a}° &rarr; {selectedComp.metrics_diff.knee_valgus?.video_b}°
                  </div>
                  <div className={`text-[11px] font-bold mt-0.5 ${(selectedComp.metrics_diff.knee_valgus?.diff || 0) < 0 ? "text-emerald-400" : "text-rose-400"
                    }`}>
                    {(selectedComp.metrics_diff.knee_valgus?.diff || 0) > 0 ? "+" : ""}
                    {selectedComp.metrics_diff.knee_valgus?.diff}°
                  </div>
                </div>

                {/* Trunk Lean */}
                <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Max Trunk Lean</div>
                  <div className="text-lg font-black text-white mt-1">
                    {selectedComp.metrics_diff.trunk_lean?.video_a}° &rarr; {selectedComp.metrics_diff.trunk_lean?.video_b}°
                  </div>
                  <div className={`text-[11px] font-bold mt-0.5 ${(selectedComp.metrics_diff.trunk_lean?.diff || 0) < 0 ? "text-emerald-400" : "text-rose-400"
                    }`}>
                    {(selectedComp.metrics_diff.trunk_lean?.diff || 0) > 0 ? "+" : ""}
                    {selectedComp.metrics_diff.trunk_lean?.diff}°
                  </div>
                </div>

                {/* Asymmetry */}
                <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Limb Asymmetry</div>
                  <div className="text-lg font-black text-white mt-1">
                    {selectedComp.metrics_diff.asymmetry?.video_a}° &rarr; {selectedComp.metrics_diff.asymmetry?.video_b}°
                  </div>
                  <div className={`text-[11px] font-bold mt-0.5 ${(selectedComp.metrics_diff.asymmetry?.diff || 0) < 0 ? "text-emerald-400" : "text-rose-400"
                    }`}>
                    {(selectedComp.metrics_diff.asymmetry?.diff || 0) > 0 ? "+" : ""}
                    {selectedComp.metrics_diff.asymmetry?.diff}°
                  </div>
                </div>
              </div>
            )}

            {/* Executive Biomechanical Progression, Regression & Delta Report */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-white font-bold text-base border-b border-slate-800 pb-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <span>Executive Biomechanical Progression & Regression Report</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {/* Improvements */}
                <div className="bg-emerald-950/20 rounded-xl p-3.5 border border-emerald-500/30 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 uppercase tracking-wider">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Verified Improvements ({selectedComp.improvements?.length || 0})</span>
                  </div>
                  <div className="space-y-2">
                    {selectedComp.improvements && selectedComp.improvements.length > 0 ? (
                      selectedComp.improvements.map((item: string, idx: number) => (
                        <div key={idx} className="text-xs text-emerald-200/90 leading-relaxed bg-emerald-950/40 p-2 rounded-lg border border-emerald-500/20">
                          {item}
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-slate-400 italic">No significant improvements registered.</div>
                    )}
                  </div>
                </div>

                {/* Regressions */}
                <div className="bg-rose-950/20 rounded-xl p-3.5 border border-rose-500/30 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400 uppercase tracking-wider">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Regressions & Risks ({selectedComp.deteriorations?.length || 0})</span>
                  </div>
                  <div className="space-y-2">
                    {selectedComp.deteriorations && selectedComp.deteriorations.length > 0 ? (
                      selectedComp.deteriorations.map((item: string, idx: number) => (
                        <div key={idx} className="text-xs text-rose-200/90 leading-relaxed bg-rose-950/40 p-2 rounded-lg border border-rose-500/20">
                          {item}
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-emerald-300 italic">✓ No technical regressions identified.</div>
                    )}
                  </div>
                </div>

                {/* Neutral */}
                <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 uppercase tracking-wider">
                    <Activity className="w-3.5 h-3.5" />
                    <span>Stable Baselines ({selectedComp.neutral_observations?.length || 0})</span>
                  </div>
                  <div className="space-y-2">
                    {selectedComp.neutral_observations && selectedComp.neutral_observations.length > 0 ? (
                      selectedComp.neutral_observations.map((item: string, idx: number) => (
                        <div key={idx} className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                          {item}
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-slate-500 italic">Parameters evolved across trials.</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Coaching Verdict & Action Transitions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                    <GitBranch className="w-3.5 h-3.5" />
                    Movement Demands & Action Transition
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {selectedComp.action_transition_summary || "Kinetic demands evaluated across baseline and comparison videos."}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-500/30 space-y-1">
                  <div className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Targeted Coaching Verdict & Prescription
                  </div>
                  <p className="text-xs text-indigo-200 leading-relaxed">
                    {selectedComp.detailed_coaching_verdict || "Maintain progressive resistance and unilateral limb control drills."}
                  </p>
                </div>
              </div>
            </div>

            {/* 8-Action Kinetic Recognition Matrix */}
            {Array.isArray(selectedComp.actions_comparison) && selectedComp.actions_comparison.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <h4 className="text-base font-bold text-white flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-pink-400" />
                    <span>8-Action Kinetic Recognition Matrix (Video 1 vs Video 2)</span>
                  </h4>
                  <span className="text-[10px] text-slate-400 font-mono">Automated Kinetic Classification</span>
                </div>

                <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px] bg-slate-900/60">
                        <th className="p-3 font-semibold">Target Athletic Action</th>
                        <th className="p-3 font-semibold text-indigo-300">Video 1 (Baseline)</th>
                        <th className="p-3 font-semibold text-pink-300">Video 2 (Comparison)</th>
                        <th className="p-3 font-semibold text-center">Movement Match</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {selectedComp.actions_comparison.map((row: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              <div className="p-1 rounded-md bg-slate-800">
                                {ACTION_ICONS[row.action] || <Activity className="w-3.5 h-3.5 text-slate-400" />}
                              </div>
                              <span className="font-bold text-white">{row.action}</span>
                            </div>
                          </td>

                          <td className="p-3">
                            <div className="space-y-0.5">
                              <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.video_a_performed ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-slate-800 text-slate-400"
                                  }`}>
                                  {row.video_a_performed ? "✓ PERFORMED" : "NOT DETECTED"}
                                </span>
                                <span className="font-semibold text-slate-300 text-[11px]">{row.video_a_confidence}%</span>
                              </div>
                              <div className="text-[10px] text-slate-400">{row.video_a_metric}</div>
                            </div>
                          </td>

                          <td className="p-3">
                            <div className="space-y-0.5">
                              <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.video_b_performed ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-slate-800 text-slate-400"
                                  }`}>
                                  {row.video_b_performed ? "✓ PERFORMED" : "NOT DETECTED"}
                                </span>
                                <span className="font-semibold text-slate-300 text-[11px]">{row.video_b_confidence}%</span>
                              </div>
                              <div className="text-[10px] text-slate-400">{row.video_b_metric}</div>
                            </div>
                          </td>

                          <td className="p-3 text-center">
                            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${row.match
                              ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                              : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                              }`}>
                              {row.match ? "Matched Pattern" : "Technique Delta"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 24-Point Kinetic Chain Telemetry Comparison Grid */}
            {selectedComp.kinematics_comparison && Object.keys(selectedComp.kinematics_comparison).length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <h4 className="text-base font-bold text-white flex items-center gap-2">
                    <Compass className="w-4 h-4 text-indigo-400" />
                    <span>Full Kinetic Chain Joint Angle Telemetry Comparison</span>
                  </h4>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {Object.keys(selectedComp.kinematics_comparison).length} Metric Pairs
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {Object.entries(selectedComp.kinematics_comparison).map(([key, data]: [string, any]) => {
                    const isPositiveImprovement = (key.includes("symmetry") && data.diff > 0) || (!key.includes("symmetry") && data.diff < 0);
                    return (
                      <div key={key} className="bg-slate-950/70 p-3 rounded-xl border border-slate-800 space-y-1">
                        <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider truncate">
                          {data.label}
                        </div>
                        <div className="flex items-baseline justify-between">
                          <div className="text-sm font-bold text-white">
                            <span className="text-indigo-300">{data.video_a}</span>
                            <span className="text-slate-600 mx-1">&rarr;</span>
                            <span className="text-pink-300">{data.video_b}</span>
                          </div>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${Math.abs(data.diff) < 0.1
                            ? "bg-slate-800 text-slate-400"
                            : isPositiveImprovement
                              ? "bg-emerald-500/20 text-emerald-400"
                              : "bg-rose-500/20 text-rose-400"
                            }`}>
                            {data.diff > 0 ? "+" : ""}{data.diff}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Injury Risk Distribution Breakdown */}
            {selectedComp.injury_probabilities_comparison && Object.keys(selectedComp.injury_probabilities_comparison).length > 0 && (
              <div className="space-y-3">
                <div className="border-b border-slate-800 pb-2">
                  <h4 className="text-base font-bold text-white">Injury Risk Category Comparison (%)</h4>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                  {Object.entries(selectedComp.injury_probabilities_comparison).map(([inj, data]: [string, any]) => (
                    <div key={inj} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-center space-y-1">
                      <div className="text-[10px] text-slate-400 font-bold uppercase truncate">{inj}</div>
                      <div className="text-xs font-bold text-white">
                        <span className="text-indigo-300">{data.video_a}%</span> &rarr;{" "}
                        <span className="text-pink-300">{data.video_b}%</span>
                      </div>
                      <div className={`text-[10px] font-bold ${data.diff < 0 ? "text-emerald-400" : data.diff > 0 ? "text-rose-400" : "text-slate-400"}`}>
                        {data.diff > 0 ? "+" : ""}{data.diff}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Corrective Protocol & Clinical Recommendations */}
            <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-pink-400" />
                  Prescribed Clinical Training Protocol
                </span>
                <p className="text-xs text-slate-300">
                  Targeted corrective exercises, form cues, and injury-reduction training plans are tailored for this movement pattern.
                </p>
              </div>
              <Link
                href={`/dashboard/recommendations?activity=${encodeURIComponent(selectedComp.primary_action || "Squatting")}&risk=${encodeURIComponent(selectedComp.overall_risk_level || "High Risk")}`}
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white text-xs font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] shrink-0 flex items-center gap-1.5"
              >
                <span>View Corrective Training Protocol</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Modal Bottom Footer */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setSelectedComp(null)}
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition-colors cursor-pointer"
              >
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
