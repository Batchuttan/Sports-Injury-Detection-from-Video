"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { getAnalyses, getSingleAnalysis, deleteAnalyses, downloadAnalysisPdf, downloadAnalysisCsv, API_URL } from "@/lib/api";
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
  Play,
  PlayCircle,
  Pause
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

export default function ReportsArchivePage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterRisk, setFilterRisk] = useState<string>("All");

  // Selection & Delete Mode
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [deleting, setDeleting] = useState(false);
  const [deleteMessage, setDeleteMessage] = useState("");

  // Modal State
  const [selectedAnalysis, setSelectedAnalysis] = useState<any | null>(null);
  const [loadingModalId, setLoadingModalId] = useState<number | null>(null);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingCsv, setExportingCsv] = useState(false);

  const modalVideoRef = useRef<HTMLVideoElement | null>(null);
  const [isModalPlaying, setIsModalPlaying] = useState(true);

  useEffect(() => {
    if (selectedAnalysis) {
      setIsModalPlaying(true);
      setTimeout(() => {
        if (modalVideoRef.current) {
          modalVideoRef.current.play().catch(() => { });
        }
      }, 300);
    }
  }, [selectedAnalysis]);

  const togglePlayPauseModal = () => {
    if (!modalVideoRef.current) return;
    if (isModalPlaying) {
      modalVideoRef.current.pause();
      setIsModalPlaying(false);
    } else {
      modalVideoRef.current.play().catch(() => { });
      setIsModalPlaying(true);
    }
  };

  const fetchReports = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      // Fetch all reports without overview_only filter
      const data = await getAnalyses(token, false);
      setAnalyses(data || []);
    } catch (err) {
      console.error("Failed to load reports:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleViewReport = async (analysis: any) => {
    setLoadingModalId(analysis.id);
    try {
      const token = localStorage.getItem("token");
      if (token) {
        const full = await getSingleAnalysis(token, analysis.id);
        setSelectedAnalysis(full);
      } else {
        setSelectedAnalysis(analysis);
      }
    } catch (err) {
      console.warn("Falling back to local data:", err);
      setSelectedAnalysis(analysis);
    } finally {
      setLoadingModalId(null);
    }
  };

  const handleExportPdf = async (analysisId: number, activity: string) => {
    try {
      setExportingPdf(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const safeAct = (activity || "Report").replace(/\s+/g, "_");
      await downloadAnalysisPdf(token, analysisId, `SportsAI_Report_${analysisId}_${safeAct}.pdf`);
    } catch (err: any) {
      alert("Failed to export PDF: " + err.message);
    } finally {
      setExportingPdf(false);
    }
  };

  const handleExportCsv = async (analysisId: number, activity: string) => {
    try {
      setExportingCsv(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const safeAct = (activity || "Report").replace(/\s+/g, "_");
      await downloadAnalysisCsv(token, analysisId, `SportsAI_Report_${analysisId}_${safeAct}.xlsx`);
    } catch (err: any) {
      alert("Failed to export CSV: " + err.message);
    } finally {
      setExportingCsv(false);
    }
  };

  const toggleSelectReport = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIds.size === filteredAnalyses.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredAnalyses.map((a) => a.id)));
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) return;
    const confirmDelete = window.confirm(
      `Are you sure you want to permanently delete ${selectedIds.size} selected report(s)? This action cannot be undone.`
    );
    if (!confirmDelete) return;

    try {
      setDeleting(true);
      const token = localStorage.getItem("token");
      if (!token) return;

      const idsArray = Array.from(selectedIds);
      const res = await deleteAnalyses(token, idsArray);
      setDeleteMessage(res.message || `Deleted ${idsArray.length} reports successfully.`);
      setSelectedIds(new Set());
      setIsDeleteMode(false);
      await fetchReports();
      setTimeout(() => setDeleteMessage(""), 4000);
    } catch (err: any) {
      alert("Failed to delete reports: " + err.message);
    } finally {
      setDeleting(false);
    }
  };

  const parseKinematics = (kin: any) => {
    if (!kin) return null;
    if (typeof kin === "string") {
      try {
        return JSON.parse(kin);
      } catch {
        return null;
      }
    }
    return kin;
  };

  const parseInjuryProbabilities = (probs: any) => {
    if (!probs) return [];
    let parsed = probs;
    if (typeof probs === "string") {
      try {
        parsed = JSON.parse(probs);
      } catch {
        return [];
      }
    }
    if (Array.isArray(parsed)) {
      return parsed.map((item) => (typeof item === "string" ? { label: item, value: 0 } : item));
    }
    if (typeof parsed === "object") {
      return Object.entries(parsed).map(([key, val]) => ({
        label: key,
        value: typeof val === "number" ? val : parseInt(String(val), 10) || 0,
      }));
    }
    return [];
  };

  const filteredAnalyses = analyses.filter((a) => {
    const matchesSearch =
      (a.activity || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (a.created_at || "").toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk =
      filterRisk === "All"
        ? true
        : filterRisk === "High"
          ? a.risk_score > 40
          : filterRisk === "Moderate"
            ? a.risk_score > 20 && a.risk_score <= 40
            : a.risk_score <= 20;
    return matchesSearch && matchesRisk;
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
            <span className="text-indigo-400 font-medium">Permanent Reports Archive</span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <FileText className="w-7 h-7 text-indigo-400 shrink-0" />
            <span>Biomechanics & Kinetic Reports Archive</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Permanent record of all historical video motion analyses with microscopic joint angle telemetry and anomaly detection.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/upload"
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] shrink-0 flex items-center gap-1.5"
          >
            <Activity className="w-4 h-4" />
            <span>Analyze New Video</span>
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
            placeholder="Search activity, date..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900/80 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
          <div className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400 ml-2" />
            {["All", "High", "Moderate", "Low"].map((level) => (
              <button
                key={level}
                onClick={() => setFilterRisk(level)}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors cursor-pointer ${filterRisk === level ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                  }`}
              >
                {level === "All" ? "All Risks" : `${level} Risk`}
              </button>
            ))}
          </div>

          <span className="text-xs text-slate-500 font-mono bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800 shrink-0">
            {filteredAnalyses.length} Archive Reports
          </span>
        </div>
      </div>

      {/* Reports Grid */}
      {loading ? (
        <div className="glass-panel p-20 rounded-3xl border border-slate-800 text-center flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-slate-400">Loading permanent report archive...</span>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="glass-panel p-16 rounded-3xl border border-slate-800 text-center space-y-3">
          <FileText className="w-10 h-10 text-slate-600 mx-auto" />
          <h4 className="text-base font-bold text-white">No reports match your filters</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Try adjusting your search query or upload a new athletic video to generate telemetry assessments.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAnalyses.map((analysis) => {
            const kin = parseKinematics(analysis.kinematics);
            const probs = parseInjuryProbabilities(analysis.injury_probabilities);
            const isSelected = selectedIds.has(analysis.id);

            return (
              <div
                key={analysis.id}
                onClick={() => isDeleteMode && toggleSelectReport(analysis.id)}
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
                      <div className="text-white font-bold text-base flex items-center gap-2">
                        <span>{analysis.activity}</span>
                        <span className="text-[10px] text-slate-500 font-mono">#{analysis.id}</span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {new Date(analysis.created_at).toLocaleDateString()} • {new Date(analysis.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {analysis.video_url && (
                        <span className="hidden sm:inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 font-semibold">
                          <Play className="w-2.5 h-2.5 fill-indigo-300" />
                          Footage
                        </span>
                      )}
                      <div
                        className={`px-2.5 py-1 rounded-xl text-xs font-extrabold shrink-0 border ${analysis.risk_score > 40
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                          : analysis.risk_score > 20
                            ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                            : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          }`}
                      >
                        {analysis.risk_score} Risk
                      </div>
                    </div>
                  </div>

                  {/* Microscopic Telemetry Preview */}
                  {kin && (
                    <div className="grid grid-cols-3 gap-1.5 p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-[11px]">
                      <div>
                        <span className="text-slate-500 block text-[10px]">Valgus FPPA</span>
                        <strong className={Math.max(kin.valgus_l_max || 0, kin.valgus_r_max || 0) > 15 ? "text-rose-400" : "text-emerald-400"}>
                          {Math.max(kin.valgus_l_max || 0, kin.valgus_r_max || 0)}°
                        </strong>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px]">Trunk Lean</span>
                        <strong className={(kin.trunk_lean_max || 0) > 30 ? "text-rose-400" : "text-slate-200"}>
                          {kin.trunk_lean_max || kin.trunk_lean_mean || 0}°
                        </strong>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px]">Symmetry</span>
                        <strong className="text-indigo-400">
                          {kin.bilateral_symmetry_index || 94}%
                        </strong>
                      </div>
                    </div>
                  )}

                  {/* Flags & Probabilities */}
                  <div className="space-y-1.5">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                      <span>Anomalies & Flags</span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        {probs.length > 0 ? `${probs.length} flags` : "None"}
                      </span>
                    </div>

                    <div className="space-y-1">
                      {probs.slice(0, 3).map((item, idx) => (
                        <div key={idx} className="text-xs text-slate-300 flex items-center justify-between">
                          <span className="flex items-center gap-1.5 truncate">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0"></span>
                            <span className="truncate">{item.label}</span>
                          </span>
                          {item.value > 0 && (
                            <span className="font-bold font-mono text-[11px] text-rose-300 ml-2">
                              {item.value}%
                            </span>
                          )}
                        </div>
                      ))}
                      {probs.length > 3 && (
                        <div className="text-[10px] text-indigo-400 font-medium">
                          +{probs.length - 3} additional anomalies...
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Corrective Recommendation Snippet */}
                  <div className="pt-2">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                      Prescribed Recommendation
                    </div>
                    <div className="text-xs text-indigo-300 bg-indigo-500/10 p-2.5 rounded-xl border border-indigo-500/20 line-clamp-2">
                      {analysis.corrective_recommendation || "Maintain progressive resistance and symmetry balance."}
                    </div>
                  </div>
                </div>

                {/* Card Action Buttons: Prominent VIEW Button */}
                <div className="pt-3 border-t border-slate-800/80">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewReport(analysis);
                    }}
                    disabled={loadingModalId === analysis.id}
                    className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-bold text-xs rounded-xl shadow-[0_0_15px_rgba(79,70,229,0.3)] transition-all flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <Eye className="w-4 h-4 shrink-0" />
                    <span>{loadingModalId === analysis.id ? "Loading Telemetry..." : "VIEW FULL DETAILS & TELEMETRY"}</span>
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
                  <CheckSquare className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{selectedIds.size === filteredAnalyses.length ? "Deselect All" : "Select All"}</span>
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

      {/* Comprehensive Biomechanics Lab Report Modal */}
      {selectedAnalysis && (() => {
        const kin = parseKinematics(selectedAnalysis.kinematics) || {};
        const probs = parseInjuryProbabilities(selectedAnalysis.injury_probabilities);

        return (
          <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto animate-fadeIn">
            <div className="glass-panel w-full max-w-4xl max-h-[94vh] rounded-3xl border border-slate-700 p-6 sm:p-8 overflow-y-auto space-y-6 relative shadow-[0_0_60px_rgba(0,0,0,0.9)]">
              {/* Modal Header with Top-Right Export PDF and Export CSV Buttons */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <h3 className="text-2xl font-extrabold text-white">
                      {selectedAnalysis.activity} Biomechanical Telemetry
                    </h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-extrabold border ${selectedAnalysis.risk_score > 40
                        ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                        : selectedAnalysis.risk_score > 20
                          ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                          : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        }`}
                    >
                      {selectedAnalysis.risk_score} / 100 Risk ({selectedAnalysis.risk_level})
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 font-mono">
                    Report #{selectedAnalysis.id} • Analyzed on {new Date(selectedAnalysis.created_at).toLocaleString()}
                  </p>
                </div>

                {/* Top-Right Action Controls: Export PDF, Export CSV, and Close */}
                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <button
                    type="button"
                    onClick={() => handleExportPdf(selectedAnalysis.id, selectedAnalysis.activity)}
                    disabled={exportingPdf}
                    className="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-slate-950 hover:to-slate-950 hover:bg-slate-950 text-white hover:text-purple-200 rounded-xl text-xs font-bold transition-all shadow-[0_0_16px_rgba(168,85,247,0.45)] hover:shadow-[0_0_14px_rgba(147,51,234,0.35)] border border-purple-400/40 hover:border-purple-500 flex items-center gap-1.5 cursor-pointer disabled:opacity-50 group"
                    title="Export single video clinical biomechanics report as PDF"
                  >
                    <Download className="w-3.5 h-3.5 text-white group-hover:text-purple-300 transition-colors" />
                    <span>{exportingPdf ? "Generating PDF..." : "Export PDF"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleExportCsv(selectedAnalysis.id, selectedAnalysis.activity)}
                    disabled={exportingCsv}
                    className="px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-slate-950 hover:to-slate-950 hover:bg-slate-950 text-white hover:text-purple-200 rounded-xl text-xs font-bold transition-all shadow-[0_0_16px_rgba(168,85,247,0.45)] hover:shadow-[0_0_14px_rgba(147,51,234,0.35)] border border-purple-400/40 hover:border-purple-500 flex items-center gap-1.5 cursor-pointer disabled:opacity-50 group"
                    title="Export structured joint kinematics & clinical metrics with customized column widths"
                  >
                    <Download className="w-3.5 h-3.5 text-white group-hover:text-purple-300 transition-colors" />
                    <span>{exportingCsv ? "Exporting CSV..." : "Export CSV"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedAnalysis(null)}
                    className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors cursor-pointer"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Analyzed Movement Video Telemetry Player */}
              {(() => {
                const videoSrc = resolveVideoSrc(selectedAnalysis.video_url || (selectedAnalysis as any).processed_url);
                if (!videoSrc) return null;
                return (
                  <div className="bg-slate-950/80 rounded-2xl border border-slate-800 p-4 space-y-3 shadow-inner">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                      <div className="flex items-center gap-2 flex-wrap">
                        <PlayCircle className="w-4 h-4 text-indigo-400" />
                        <span className="font-bold text-white">Analyzed Movement Footage & Skeleton Telemetry</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-semibold flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          Hardware Accelerated (GMeet Ready)
                        </span>
                      </div>
                      <div className="flex items-center gap-2 self-start sm:self-auto">
                        <button
                          type="button"
                          onClick={togglePlayPauseModal}
                          className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white rounded-lg transition-all shadow-[0_0_12px_rgba(99,102,241,0.4)] flex items-center gap-1.5 cursor-pointer"
                        >
                          {isModalPlaying ? (
                            <>
                              <Pause className="w-3.5 h-3.5" />
                              <span>Pause</span>
                            </>
                          ) : (
                            <>
                              <Play className="w-3.5 h-3.5 fill-white" />
                              <span>Resume</span>
                            </>
                          )}
                        </button>
                        <a
                          href={videoSrc}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1"
                        >
                          <span>Open Raw MP4</span>
                          <span>↗</span>
                        </a>
                      </div>
                    </div>

                    <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800/80 relative flex items-center justify-center">
                      <video
                        ref={modalVideoRef}
                        key={videoSrc}
                        src={videoSrc}
                        controls
                        autoPlay
                        loop
                        muted
                        playsInline
                        preload="auto"
                        crossOrigin="anonymous"
                        disablePictureInPicture
                        onPlay={() => setIsModalPlaying(true)}
                        onPause={() => setIsModalPlaying(false)}
                        className="w-full h-full object-contain transform-gpu"
                        style={{ transform: "translateZ(0)", willChange: "transform", backfaceVisibility: "hidden" }}
                      >
                        Your browser does not support HTML5 video playback.
                      </video>
                    </div>
                  </div>
                );
              })()}

              {/* Section 1: Dynamic Knee Valgus (FPPA) & Hip Flexion */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-400">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <span>Section 1: Dynamic Knee Valgus (FPPA) & Hip Flexion (degrees)</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Left Knee Valgus (Mean)</span>
                    <strong className="text-white text-base">{kin.valgus_l_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Peak: {kin.valgus_l_max ?? 0}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Right Knee Valgus (Mean)</span>
                    <strong className="text-white text-base">{kin.valgus_r_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Peak: {kin.valgus_r_max ?? 0}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Left Hip Flexion (Mean)</span>
                    <strong className="text-white text-base">{kin.hip_flexion_l_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Sagittal plane hinge</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Right Hip Flexion (Mean)</span>
                    <strong className="text-white text-base">{kin.hip_flexion_r_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Sagittal plane hinge</span>
                  </div>
                </div>
              </div>

              {/* Section 2: Knee Flexion Angle Range of Motion */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-400">
                  <Compass className="w-4 h-4 text-indigo-400" />
                  <span>Section 2: Knee Flexion Range of Motion (degrees)</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Left Knee Deepest Angle</span>
                    <strong className="text-white text-base">{kin.knee_flexion_l_min ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Mean: {kin.knee_flexion_l_mean ?? 0}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Right Knee Deepest Angle</span>
                    <strong className="text-white text-base">{kin.knee_flexion_r_min ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Mean: {kin.knee_flexion_r_mean ?? 0}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Left Knee Extension ROM</span>
                    <strong className="text-white text-base">{kin.knee_flexion_l_max ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Active extension span</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Right Knee Extension ROM</span>
                    <strong className="text-white text-base">{kin.knee_flexion_r_max ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Active extension span</span>
                  </div>
                </div>
              </div>

              {/* Section 3: Postural Tilts, Rotations & Axial Alignments */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-pink-400">
                  <Sparkles className="w-4 h-4 text-pink-400" />
                  <span>Section 3: Postural Tilts, Rotations & Axial Alignments (degrees)</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Head & Neck Tilt</span>
                    <strong className="text-white text-base">{kin.head_tilt_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Max: {kin.head_tilt_max ?? 0}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Trunk Sagittal Lean</span>
                    <strong className="text-white text-base">{kin.trunk_lean_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Max: {kin.trunk_lean_max ?? 0}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Pelvic Tilt (Horizontal)</span>
                    <strong className="text-white text-base">{kin.pelvic_tilt_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Coronal acute level</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Shoulder Coronal Tilt</span>
                    <strong className="text-white text-base">{kin.shoulder_tilt_mean ?? 0}°</strong>
                    <span className="text-[10px] text-slate-500 block">Torso rotation</span>
                  </div>
                </div>
              </div>

              {/* Section 4: Velocities, Ground Shock & Symmetry */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <span>Section 4: Joint Velocities, Impact Deceleration & Bilateral Symmetry</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Peak Wrist Velocity</span>
                    <strong className="text-white text-base">{kin.peak_wrist_velocity ?? 0} H/s</strong>
                    <span className="text-[10px] text-slate-500 block">Hand kinetic drive</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Peak Ankle Velocity</span>
                    <strong className="text-white text-base">{kin.peak_ankle_velocity ?? 0} H/s</strong>
                    <span className="text-[10px] text-slate-500 block">Stride swing speed</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Touchdown Deceleration</span>
                    <strong className="text-white text-base">{kin.estimated_impact_g ?? 1.2} G</strong>
                    <span className="text-[10px] text-slate-500 block">Shock absorption</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Bilateral Symmetry</span>
                    <strong className="text-indigo-400 text-base">{kin.bilateral_symmetry_index ?? 94}%</strong>
                    <span className="text-[10px] text-slate-500 block">Asymmetry: {kin.limb_asymmetry_deg ?? 0}°</span>
                  </div>
                </div>
              </div>

              {/* Section 5: Specific Injury Probabilities */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-rose-400">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <span>Section 5: Specific Kinetic Injury Risk Probabilities</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {probs.map((p, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                      <span className="text-xs text-slate-300 font-medium">{p.label}</span>
                      <span className={`text-xs font-extrabold font-mono ${p.value > 40 ? "text-rose-400" : p.value > 20 ? "text-amber-400" : "text-emerald-400"}`}>
                        {p.value}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Section 6: Corrective Prescription */}
              <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 space-y-2">
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center justify-between">
                  <span>Section 6: Corrective Recommendation & Clinical Prescription</span>
                  <Link
                    href={`/dashboard/recommendations?activity=${encodeURIComponent(selectedAnalysis.activity)}&risk=${encodeURIComponent(selectedAnalysis.risk_level)}`}
                    className="text-[11px] text-pink-400 hover:text-pink-300 underline font-semibold cursor-pointer"
                  >
                    View In-Depth Activity Prescription &rarr;
                  </Link>
                </div>
                <p className="text-xs text-indigo-200/90 leading-relaxed">
                  {selectedAnalysis.corrective_recommendation || "Maintain progressive resistance and symmetry balance."}
                </p>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
