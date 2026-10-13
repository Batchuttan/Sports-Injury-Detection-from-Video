"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { compareVideos, compareExistingAnalyses, getAnalyses, API_URL } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const ACTIVITIES = [
  "Auto-Detect (AI Classification)",
  "Jumping",
  "Squatting",
  "Running",
  "Sprinting",
  "Landing",
  "Throwing",
  "Cutting Movements",
  "Sport-Specific Drills"
];

interface ComparisonResult {
  video_a: {
    id?: number;
    original_filename?: string;
    activity?: string;
    processed_url?: string;
    analytics?: any;
    risk_score?: number;
    risk_level?: string;
    injury_probabilities?: any;
  };
  video_b: {
    id?: number;
    original_filename?: string;
    activity?: string;
    processed_url?: string;
    analytics?: any;
    risk_score?: number;
    risk_level?: string;
    injury_probabilities?: any;
  };
  comparison: {
    score_diff: number;
    overall_verdict: string;
    verdict_color: string;
    summary: string;
    insights: string[];
    metrics_diff: {
      risk_score: { video_a: number; video_b: number; diff: number };
      trunk_lean: { video_a: number; video_b: number; diff: number };
      knee_valgus: { video_a: number; video_b: number; diff: number };
      asymmetry: { video_a: number; video_b: number; diff: number };
    };
    injury_probabilities_comparison: Record<string, { video_a: number; video_b: number; diff: number }>;
  };
}

export default function ComparePage() {
  const [activeTab, setActiveTab] = useState<"upload" | "existing">("upload");

  // Upload state for Video A
  const [fileA, setFileA] = useState<File | null>(null);
  const [activityA, setActivityA] = useState<string>("Auto-Detect (AI Classification)");
  const [rpeA, setRpeA] = useState<number>(5);
  const [sleepA, setSleepA] = useState<number>(5);

  // Upload state for Video B
  const [fileB, setFileB] = useState<File | null>(null);
  const [activityB, setActivityB] = useState<string>("Auto-Detect (AI Classification)");
  const [rpeB, setRpeB] = useState<number>(5);
  const [sleepB, setSleepB] = useState<number>(5);

  // Shared metadata
  const [surfaceType, setSurfaceType] = useState<string>("Indoor Hardwood");
  const [footwear, setFootwear] = useState<string>("Athletic Shoes");

  // Existing analyses state
  const [existingAnalyses, setExistingAnalyses] = useState<any[]>([]);
  const [selectedIdA, setSelectedIdA] = useState<number | null>(null);
  const [selectedIdB, setSelectedIdB] = useState<number | null>(null);
  const [loadingExisting, setLoadingExisting] = useState(false);

  // Processing & Comparison results
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);

  // Synchronized Dual Video Players control
  const videoRefA = useRef<HTMLVideoElement | null>(null);
  const videoRefB = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  // Load existing analyses for history comparison
  useEffect(() => {
    const fetchExisting = async () => {
      try {
        setLoadingExisting(true);
        const token = localStorage.getItem("token");
        if (!token) return;
        const data = await getAnalyses(token);
        setExistingAnalyses(data || []);
        if (data && data.length >= 2) {
          setSelectedIdA(data[0].id);
          setSelectedIdB(data[1].id);
        } else if (data && data.length === 1) {
          setSelectedIdA(data[0].id);
        }
      } catch (err) {
        console.error("Could not fetch analyses history:", err);
      } finally {
        setLoadingExisting(false);
      }
    };
    fetchExisting();
  }, []);

  const handleUploadCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileA || !fileB) {
      setError("Please select both Video 1 and Video 2 to compare.");
      return;
    }

    setProcessing(true);
    setError("");
    setComparisonResult(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("Please log in to run video comparison.");

      const formData = new FormData();
      formData.append("file_a", fileA);
      formData.append("file_b", fileB);
      formData.append("activity_a", activityA.startsWith("Auto-Detect") ? "Auto-Detect" : activityA);
      formData.append("activity_b", activityB.startsWith("Auto-Detect") ? "Auto-Detect" : activityB);
      formData.append("surface_type", surfaceType);
      formData.append("footwear", footwear);
      formData.append("rpe_a", rpeA.toString());
      formData.append("rpe_b", rpeB.toString());
      formData.append("sleep_quality_a", sleepA.toString());
      formData.append("sleep_quality_b", sleepB.toString());

      const res = await compareVideos(token, formData);
      setComparisonResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error running video comparison.";
      setError(msg);
    } finally {
      setProcessing(false);
    }
  };

  const handleExistingCompare = async () => {
    if (!selectedIdA || !selectedIdB) {
      setError("Please select two distinct analyses from your history.");
      return;
    }
    if (selectedIdA === selectedIdB) {
      setError("Please pick two different video sessions to compare.");
      return;
    }

    setProcessing(true);
    setError("");
    setComparisonResult(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("Please log in first.");

      const res = await compareExistingAnalyses(token, selectedIdA, selectedIdB);
      setComparisonResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Comparison failed.";
      setError(msg);
    } finally {
      setProcessing(false);
    }
  };

  // Video playback sync handlers
  const togglePlayBoth = () => {
    const vA = videoRefA.current;
    const vB = videoRefB.current;

    if (!vA && !vB) return;

    if (isPlaying) {
      vA?.pause();
      vB?.pause();
      setIsPlaying(false);
    } else {
      vA?.play();
      vB?.play();
      setIsPlaying(true);
    }
  };

  const restartBoth = () => {
    if (videoRefA.current) videoRefA.current.currentTime = 0;
    if (videoRefB.current) videoRefB.current.currentTime = 0;
  };

  const changeSpeed = (speed: number) => {
    setPlaybackSpeed(speed);
    if (videoRefA.current) videoRefA.current.playbackRate = speed;
    if (videoRefB.current) videoRefB.current.playbackRate = speed;
  };

  // Prepare recharts comparison data
  const chartData = comparisonResult
    ? Object.entries(comparisonResult.comparison.injury_probabilities_comparison || {}).map(([name, data]) => ({
      injury: name.replace(" Injury", ""),
      "Video 1": data.video_a,
      "Video 2": data.video_b,
    }))
    : [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Comparative Video Biomechanics
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/15 border border-indigo-500/30 text-indigo-400">
              Dual-Stream AI
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Analyze 2 separate videos side-by-side to track movement quality, asymmetrical variances, and injury risk evolution.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-800 self-start md:self-auto">
          <button
            onClick={() => setActiveTab("upload")}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${activeTab === "upload"
              ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]"
              : "text-slate-400 hover:text-white"
              }`}
          >
            Upload 2 Videos
          </button>
          <button
            onClick={() => setActiveTab("existing")}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${activeTab === "existing"
              ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]"
              : "text-slate-400 hover:text-white"
              }`}
          >
            Compare History ({existingAnalyses.length})
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-rose-400 hover:text-white text-xs font-bold px-2">
            Dismiss
          </button>
        </div>
      )}

      {/* Mode 1: Upload 2 Videos */}
      {activeTab === "upload" && (
        <form onSubmit={handleUploadCompare} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Dropzone Video A */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 relative group">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-md border border-indigo-500/20">
                  Video 1 • Baseline / Attempt A
                </span>
                {fileA && (
                  <span className="text-xs text-emerald-400 font-medium truncate max-w-[150px]">
                    ✓ {fileA.name}
                  </span>
                )}
              </div>

              <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-xl p-6 text-center cursor-pointer transition-colors bg-slate-900/40 relative">
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => e.target.files?.[0] && setFileA(e.target.files[0])}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <div className="w-12 h-12 bg-indigo-500/10 text-indigo-400 rounded-xl flex items-center justify-center mx-auto mb-2 border border-indigo-500/20">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div className="text-sm font-semibold text-slate-200">
                  {fileA ? fileA.name : "Select or drag Video 1"}
                </div>
                <p className="text-xs text-slate-500 mt-1">MP4, MOV, or WebM (Max 50MB)</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Movement (AI Verified)</label>
                  <select
                    value={activityA}
                    onChange={(e) => setActivityA(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {ACTIVITIES.map((act) => (
                      <option key={act} value={act}>{act}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">RPE ({rpeA}/10)</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={rpeA}
                    onChange={(e) => setRpeA(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Sleep ({sleepA}/10)</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={sleepA}
                    onChange={(e) => setSleepA(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>
              </div>
            </div>

            {/* Dropzone Video B */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 relative group">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-pink-400 bg-pink-500/10 px-2.5 py-1 rounded-md border border-pink-500/20">
                  Video 2 • Comparison / Attempt B
                </span>
                {fileB && (
                  <span className="text-xs text-emerald-400 font-medium truncate max-w-[150px]">
                    ✓ {fileB.name}
                  </span>
                )}
              </div>

              <div className="border-2 border-dashed border-slate-700 hover:border-pink-500/60 rounded-xl p-6 text-center cursor-pointer transition-colors bg-slate-900/40 relative">
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => e.target.files?.[0] && setFileB(e.target.files[0])}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <div className="w-12 h-12 bg-pink-500/10 text-pink-400 rounded-xl flex items-center justify-center mx-auto mb-2 border border-pink-500/20">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div className="text-sm font-semibold text-slate-200">
                  {fileB ? fileB.name : "Select or drag Video 2"}
                </div>
                <p className="text-xs text-slate-500 mt-1">MP4, MOV, or WebM (Max 50MB)</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Movement (AI Verified)</label>
                  <select
                    value={activityB}
                    onChange={(e) => setActivityB(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-pink-500"
                  >
                    {ACTIVITIES.map((act) => (
                      <option key={act} value={act}>{act}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">RPE ({rpeB}/10)</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={rpeB}
                    onChange={(e) => setRpeB(Number(e.target.value))}
                    className="w-full accent-pink-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Sleep ({sleepB}/10)</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={sleepB}
                    onChange={(e) => setSleepB(Number(e.target.value))}
                    className="w-full accent-pink-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Environmental Settings */}
          <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-6 w-full sm:w-auto">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Surface Type</label>
                <select
                  value={surfaceType}
                  onChange={(e) => setSurfaceType(e.target.value)}
                  className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
                >
                  <option value="Indoor Hardwood">Indoor Hardwood</option>
                  <option value="Artificial Turf">Artificial Turf</option>
                  <option value="Natural Grass">Natural Grass</option>
                  <option value="Synthetic Track">Synthetic Track</option>
                  <option value="Concrete/Asphalt">Concrete/Asphalt</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Footwear</label>
                <select
                  value={footwear}
                  onChange={(e) => setFootwear(e.target.value)}
                  className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
                >
                  <option value="Athletic Shoes">Athletic Shoes</option>
                  <option value="Cleats">Cleats</option>
                  <option value="Cushioned Running Shoes">Cushioned Running Shoes</option>
                  <option value="Minimalist / Barefoot">Minimalist / Barefoot</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={processing || !fileA || !fileB}
              className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 disabled:opacity-40 text-white font-bold rounded-xl transition-all shadow-[0_0_25px_rgba(79,70,229,0.4)] flex items-center justify-center gap-2"
            >
              {processing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing Biomechanics in Parallel...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Execute Dual Video Comparison &rarr;
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Mode 2: Existing History Comparison */}
      {activeTab === "existing" && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white mb-1">Select from Recorded Movement History</h3>
            <p className="text-slate-400 text-sm">
              Pick any two recorded sessions from your database to perform immediate comparative biomechanical analysis without re-uploading.
            </p>
          </div>

          {loadingExisting ? (
            <div className="py-8 text-center text-slate-400 text-sm">Loading historical sessions...</div>
          ) : existingAnalyses.length < 2 ? (
            <div className="py-8 text-center text-slate-400 text-sm">
              You need at least 2 recorded video analyses to compare from history. Please use the "Upload 2 Videos" tab above to run a comparison.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                  Select Baseline (Video A)
                </label>
                <select
                  value={selectedIdA || ""}
                  onChange={(e) => setSelectedIdA(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  {existingAnalyses.map((ana) => (
                    <option key={ana.id} value={ana.id}>
                      #{ana.id} • {ana.activity} (Risk: {ana.risk_score}/100, {ana.risk_level}) - {new Date(ana.created_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-pink-400">
                  Select Target (Video B)
                </label>
                <select
                  value={selectedIdB || ""}
                  onChange={(e) => setSelectedIdB(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-pink-500"
                >
                  {existingAnalyses.map((ana) => (
                    <option key={ana.id} value={ana.id}>
                      #{ana.id} • {ana.activity} (Risk: {ana.risk_score}/100, {ana.risk_level}) - {new Date(ana.created_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {existingAnalyses.length >= 2 && (
            <div className="pt-2 flex justify-end">
              <button
                onClick={handleExistingCompare}
                disabled={processing || selectedIdA === selectedIdB}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-xl text-sm transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] flex items-center gap-2"
              >
                {processing ? "Comparing Datasets..." : "Compare Selected Sessions &rarr;"}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Comparison Results Presentation */}
      {comparisonResult && (
        <div className="space-y-8 animate-fadeIn">
          {/* Executive Verdict Banner */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 relative overflow-hidden">
            <div
              className={`absolute top-0 left-0 w-2 h-full ${comparisonResult.comparison.score_diff < 0
                ? "bg-emerald-500"
                : comparisonResult.comparison.score_diff > 0
                  ? "bg-rose-500"
                  : "bg-amber-500"
                }`}
            />
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pl-3">
              <div>
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${comparisonResult.comparison.verdict_color === "emerald"
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      : comparisonResult.comparison.verdict_color === "rose"
                        ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                        : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                      }`}
                  >
                    {comparisonResult.comparison.overall_verdict}
                  </span>
                  <span className="text-slate-400 text-sm">
                    Net Score Delta:{" "}
                    <strong
                      className={
                        comparisonResult.comparison.score_diff < 0
                          ? "text-emerald-400"
                          : comparisonResult.comparison.score_diff > 0
                            ? "text-rose-400"
                            : "text-slate-200"
                      }
                    >
                      {comparisonResult.comparison.score_diff > 0 ? "+" : ""}
                      {comparisonResult.comparison.score_diff} pts
                    </strong>
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white mt-2">
                  {comparisonResult.comparison.summary}
                </h3>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="text-right">
                  <div className="text-xs text-indigo-400 font-semibold uppercase">Video 1</div>
                  <div className="text-2xl font-black text-white">
                    {comparisonResult.comparison.metrics_diff.risk_score.video_a}
                    <span className="text-xs text-slate-500 font-normal">/100</span>
                  </div>
                </div>
                <div className="text-slate-600 text-xl font-bold">&rarr;</div>
                <div className="text-left">
                  <div className="text-xs text-pink-400 font-semibold uppercase">Video 2</div>
                  <div className="text-2xl font-black text-white">
                    {comparisonResult.comparison.metrics_diff.risk_score.video_b}
                    <span className="text-xs text-slate-500 font-normal">/100</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Synchronized Dual Video Players (if video URLs exist) */}
          {(comparisonResult.video_a.processed_url || comparisonResult.video_b.processed_url) && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h4 className="text-base font-bold text-white">Synchronized Movement Playback</h4>
                </div>

                {/* Master Playback Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={togglePlayBoth}
                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5"
                  >
                    {isPlaying ? (
                      <>
                        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" /></svg>
                        Pause Both
                      </>
                    ) : (
                      <>
                        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
                        Play Both
                      </>
                    )}
                  </button>
                  <button
                    onClick={restartBoth}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition-colors"
                  >
                    Restart
                  </button>
                  <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800">
                    {[0.5, 1, 1.5].map((spd) => (
                      <button
                        key={spd}
                        onClick={() => changeSpeed(spd)}
                        className={`px-2 py-1 text-xs rounded font-medium transition-colors ${playbackSpeed === spd ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
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
                        Video 1: {comparisonResult.video_a.analytics?.activity_analyzed || comparisonResult.video_a.original_filename || comparisonResult.video_a.activity}
                      </span>
                      {comparisonResult.video_a.analytics?.action_auto_corrected && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          Auto-Corrected
                        </span>
                      )}
                    </div>
                    <span className="text-slate-400">
                      Score: {comparisonResult.comparison.metrics_diff.risk_score.video_a}/100
                    </span>
                  </div>
                  <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative">
                    {comparisonResult.video_a.processed_url ? (
                      <video
                        ref={videoRefA}
                        src={`${API_URL}${comparisonResult.video_a.processed_url}`}
                        controls
                        playsInline
                        className="w-full h-full object-contain"
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
                        Video 2: {comparisonResult.video_b.analytics?.activity_analyzed || comparisonResult.video_b.original_filename || comparisonResult.video_b.activity}
                      </span>
                      {comparisonResult.video_b.analytics?.action_auto_corrected && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          Auto-Corrected
                        </span>
                      )}
                    </div>
                    <span className="text-slate-400">
                      Score: {comparisonResult.comparison.metrics_diff.risk_score.video_b}/100
                    </span>
                  </div>
                  <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative">
                    {comparisonResult.video_b.processed_url ? (
                      <video
                        ref={videoRefB}
                        src={`${API_URL}${comparisonResult.video_b.processed_url}`}
                        controls
                        playsInline
                        className="w-full h-full object-contain"
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
          )}

          {/* Metrics Diff Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Risk Score */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Risk Score</div>
              <div className="flex items-baseline justify-between">
                <div className="text-2xl font-black text-white">
                  {comparisonResult.comparison.metrics_diff.risk_score.video_a} &rarr; {comparisonResult.comparison.metrics_diff.risk_score.video_b}
                </div>
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded ${comparisonResult.comparison.metrics_diff.risk_score.diff < 0
                    ? "bg-emerald-500/20 text-emerald-400"
                    : comparisonResult.comparison.metrics_diff.risk_score.diff > 0
                      ? "bg-rose-500/20 text-rose-400"
                      : "bg-slate-700 text-slate-300"
                    }`}
                >
                  {comparisonResult.comparison.metrics_diff.risk_score.diff > 0 ? "+" : ""}
                  {comparisonResult.comparison.metrics_diff.risk_score.diff}
                </span>
              </div>
              <div className="text-[11px] text-slate-500">
                {comparisonResult.comparison.metrics_diff.risk_score.diff < 0 ? "Lower injury susceptibility" : "Increased joint strain"}
              </div>
            </div>

            {/* Knee Valgus */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Max Knee Valgus</div>
              <div className="flex items-baseline justify-between">
                <div className="text-2xl font-black text-white">
                  {comparisonResult.comparison.metrics_diff.knee_valgus.video_a}° &rarr; {comparisonResult.comparison.metrics_diff.knee_valgus.video_b}°
                </div>
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded ${comparisonResult.comparison.metrics_diff.knee_valgus.diff < 0
                    ? "bg-emerald-500/20 text-emerald-400"
                    : comparisonResult.comparison.metrics_diff.knee_valgus.diff > 0
                      ? "bg-rose-500/20 text-rose-400"
                      : "bg-slate-700 text-slate-300"
                    }`}
                >
                  {comparisonResult.comparison.metrics_diff.knee_valgus.diff > 0 ? "+" : ""}
                  {comparisonResult.comparison.metrics_diff.knee_valgus.diff}°
                </span>
              </div>
              <div className="text-[11px] text-slate-500">
                {comparisonResult.comparison.metrics_diff.knee_valgus.diff < 0 ? "Reduced ACL shear load" : "Medial collapse observed"}
              </div>
            </div>

            {/* Trunk Lean */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Max Trunk Lean</div>
              <div className="flex items-baseline justify-between">
                <div className="text-2xl font-black text-white">
                  {comparisonResult.comparison.metrics_diff.trunk_lean.video_a}° &rarr; {comparisonResult.comparison.metrics_diff.trunk_lean.video_b}°
                </div>
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded ${comparisonResult.comparison.metrics_diff.trunk_lean.diff < 0
                    ? "bg-emerald-500/20 text-emerald-400"
                    : comparisonResult.comparison.metrics_diff.trunk_lean.diff > 0
                      ? "bg-rose-500/20 text-rose-400"
                      : "bg-slate-700 text-slate-300"
                    }`}
                >
                  {comparisonResult.comparison.metrics_diff.trunk_lean.diff > 0 ? "+" : ""}
                  {comparisonResult.comparison.metrics_diff.trunk_lean.diff}°
                </span>
              </div>
              <div className="text-[11px] text-slate-500">
                {comparisonResult.comparison.metrics_diff.trunk_lean.diff < 0 ? "Upright spinal stability" : "Compensatory trunk flexion"}
              </div>
            </div>

            {/* Asymmetry */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Limb Asymmetry</div>
              <div className="flex items-baseline justify-between">
                <div className="text-2xl font-black text-white">
                  {comparisonResult.comparison.metrics_diff.asymmetry.video_a}° &rarr; {comparisonResult.comparison.metrics_diff.asymmetry.video_b}°
                </div>
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded ${comparisonResult.comparison.metrics_diff.asymmetry.diff < 0
                    ? "bg-emerald-500/20 text-emerald-400"
                    : comparisonResult.comparison.metrics_diff.asymmetry.diff > 0
                      ? "bg-rose-500/20 text-rose-400"
                      : "bg-slate-700 text-slate-300"
                    }`}
                >
                  {comparisonResult.comparison.metrics_diff.asymmetry.diff > 0 ? "+" : ""}
                  {comparisonResult.comparison.metrics_diff.asymmetry.diff}°
                </span>
              </div>
              <div className="text-[11px] text-slate-500">
                {comparisonResult.comparison.metrics_diff.asymmetry.diff < 0 ? "Balanced bilateral load" : "Asymmetric limb favoring"}
              </div>
            </div>
          </div>

          {/* Injury Probabilities Comparative Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div>
                <h4 className="text-base font-bold text-white">Injury Risk Probabilities Comparison (%)</h4>
                <p className="text-xs text-slate-400">Comparing risk distribution across specific kinetic injury categories.</p>
              </div>

              <div className="h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="injury" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#334155",
                        borderRadius: "8px",
                        color: "#f8fafc"
                      }}
                    />
                    <Legend />
                    <Bar dataKey="Video 1" fill="#6366f1" radius={[4, 4, 0, 0]} name="Video 1 (Baseline)" />
                    <Bar dataKey="Video 2" fill="#ec4899" radius={[4, 4, 0, 0]} name="Video 2 (Comparison)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Insights & Coaching takeaways */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between">
              <div>
                <h4 className="text-base font-bold text-white mb-3">AI Biomechanical Takeaways</h4>
                <div className="space-y-3">
                  {comparisonResult.comparison.insights.map((insight, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                      <span className="leading-relaxed">{insight}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800">
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Action Recommendation
                </div>
                <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 leading-relaxed">
                  {comparisonResult.video_b.analytics?.corrective_recommendation ||
                    "Maintain progressive resistance drills while monitoring bilateral limb loading balance."}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
