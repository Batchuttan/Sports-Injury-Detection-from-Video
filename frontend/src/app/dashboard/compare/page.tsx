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
import {
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  XCircle,
  ArrowUpCircle,
  ArrowDownCircle,
  Footprints,
  Zap,
  Target,
  ShieldCheck,
  GitBranch,
  Activity,
  Compass,
  Volume2,
  VolumeX,
  Play,
  Pause,
  RotateCcw,
  GitCompare,
  FileText,
  ArrowRight
} from "lucide-react";

const ACTIVITIES = [
  "Auto-Detect (AI Classification)",
  "Jumping",
  "Squatting",
  "Sprinting",
  "Landing",
  "Throwing",
  "Cutting Movements",
  "Sports Specific Drills"
];

const ACTION_ICONS: Record<string, React.ReactNode> = {
  "Jumping": <ArrowUpCircle className="w-4 h-4 text-sky-400" />,
  "Squatting": <ArrowDownCircle className="w-4 h-4 text-indigo-400" />,
  "Sprinting": <Zap className="w-4 h-4 text-amber-400" />,
  "Landing": <ShieldCheck className="w-4 h-4 text-teal-400" />,
  "Throwing": <Target className="w-4 h-4 text-rose-400" />,
  "Cutting Movements": <GitBranch className="w-4 h-4 text-violet-400" />,
  "Sports Specific Drills": <Activity className="w-4 h-4 text-orange-400" />
};

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
    improvements?: string[];
    deteriorations?: string[];
    neutral_observations?: string[];
    action_transition_summary?: string;
    detailed_coaching_verdict?: string;
    is_identical_video?: boolean;
    identical_video_message?: string;
    is_cross_activity?: boolean;
    cross_activity_message?: string;
    actions_comparison?: Array<{
      action: string;
      video_a_performed: boolean;
      video_a_confidence: number;
      video_a_metric: string;
      video_b_performed: boolean;
      video_b_confidence: number;
      video_b_metric: string;
      match: boolean;
    }>;
    kinematics_comparison?: Record<string, {
      label: string;
      video_a: number;
      video_b: number;
      diff: number;
    }>;
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
  const [isPlaying, setIsPlaying] = useState(true);
  const [isPlayingA, setIsPlayingA] = useState(true);
  const [isPlayingB, setIsPlayingB] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  useEffect(() => {
    if (comparisonResult) {
      setIsPlaying(true);
      setIsPlayingA(true);
      setIsPlayingB(true);
      setTimeout(() => {
        if (videoRefA.current) videoRefA.current.play().catch(() => { });
        if (videoRefB.current) videoRefB.current.play().catch(() => { });
      }, 300);
    }
  }, [comparisonResult]);

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

  const resolveVideoSrc = (url?: string) => {
    if (!url) return "";
    if (url.startsWith("http://") || url.startsWith("https://")) return url;
    const clean = url.startsWith("/") ? url : `/${url}`;
    return `${API_URL}${clean}`;
  };

  // Video playback sync handlers
  const togglePlayBoth = async () => {
    const vA = videoRefA.current;
    const vB = videoRefB.current;

    if (!vA && !vB) return;

    if (isPlaying) {
      vA?.pause();
      vB?.pause();
      setIsPlaying(false);
    } else {
      // If either video is finished or near the end, reset to start
      if (vA && (vA.ended || vA.currentTime >= (vA.duration - 0.2))) {
        vA.currentTime = 0;
      }
      if (vB && (vB.ended || vB.currentTime >= (vB.duration - 0.2))) {
        vB.currentTime = 0;
      }

      try {
        if (vA) {
          try {
            await vA.play();
          } catch (errA) {
            console.warn("Video 1 unmuted play blocked, falling back to muted play:", errA);
            vA.muted = true;
            await vA.play();
          }
        }
        if (vB) {
          try {
            await vB.play();
          } catch (errB) {
            console.warn("Video 2 unmuted play blocked, falling back to muted play:", errB);
            vB.muted = true;
            await vB.play();
          }
        }
        setIsPlaying(true);
      } catch (err) {
        console.error("Playback error:", err);
      }
    }
  };

  const restartBoth = () => {
    if (videoRefA.current) {
      videoRefA.current.currentTime = 0;
    }
    if (videoRefB.current) {
      videoRefB.current.currentTime = 0;
    }
    setIsPlaying(false);
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

  const playSingleVideo = async (video: "A" | "B") => {
    const target = video === "A" ? videoRefA.current : videoRefB.current;
    if (!target) return;
    if (target.paused) {
      if (target.ended || target.currentTime >= (target.duration - 0.2)) {
        target.currentTime = 0;
      }
      try {
        await target.play();
      } catch {
        target.muted = true;
        await target.play();
      }
      if (video === "A") setIsPlayingA(true);
      else setIsPlayingB(true);
    } else {
      target.pause();
      if (video === "A") setIsPlayingA(false);
      else setIsPlayingB(false);
    }
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
          {/* Identical Video Upload Notice */}
          {comparisonResult.comparison.is_identical_video && (
            <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-2 flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-base font-bold text-amber-300">Identical Video Recording Detected</h4>
                <p className="text-xs text-amber-200/90 leading-relaxed">
                  {comparisonResult.comparison.identical_video_message}
                </p>
              </div>
            </div>
          )}

          {/* Cross-Activity Discrepancy Notice */}
          {comparisonResult.comparison.is_cross_activity && (
            <div className="p-6 rounded-2xl bg-sky-500/10 border border-sky-500/30 text-sky-200 space-y-2 flex items-start gap-4">
              <Sparkles className="w-6 h-6 text-sky-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-base font-bold text-sky-300">Cross-Activity Movement Discrepancy</h4>
                <p className="text-xs text-sky-200/90 leading-relaxed">
                  {comparisonResult.comparison.cross_activity_message}
                </p>
              </div>
            </div>
          )}

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
          {(() => {
            const urlA = resolveVideoSrc(comparisonResult.video_a.processed_url || (comparisonResult.video_a as any).video_url);
            const urlB = resolveVideoSrc(comparisonResult.video_b.processed_url || (comparisonResult.video_b as any).video_url);

            if (!urlA && !urlB) return null;

            return (
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h4 className="text-base font-bold text-white">Synchronized Movement Playback</h4>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold rounded-md">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      ⚡ Low-Latency Hardware Accelerated (GMeet Ready)
                    </span>
                  </div>

                  {/* Master Playback Controls */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <button
                      type="button"
                      onClick={togglePlayBoth}
                      className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer shadow-[0_0_15px_rgba(99,102,241,0.3)]"
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
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition-colors flex items-center gap-1 cursor-pointer"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Restart</span>
                    </button>
                    <button
                      type="button"
                      onClick={toggleMuteBoth}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors flex items-center gap-1 cursor-pointer ${isMuted
                        ? "bg-slate-800 text-slate-300 border-slate-700 hover:text-white"
                        : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        }`}
                    >
                      {isMuted ? <VolumeX className="w-3.5 h-3.5 text-slate-400" /> : <Volume2 className="w-3.5 h-3.5 text-emerald-400" />}
                      <span>{isMuted ? "Muted" : "Audio On"}</span>
                    </button>
                    <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800">
                      {[0.5, 1, 1.5].map((spd) => (
                        <button
                          type="button"
                          key={spd}
                          onClick={() => changeSpeed(spd)}
                          className={`px-2 py-1 text-xs rounded font-medium transition-colors cursor-pointer ${playbackSpeed === spd ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
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
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => playSingleVideo("A")}
                          className="px-2 py-0.5 rounded bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 text-[10px] font-bold cursor-pointer"
                        >
                          {isPlayingA ? "Pause" : "Resume"}
                        </button>
                        <span className="text-slate-400">
                          Score: {comparisonResult.comparison.metrics_diff.risk_score.video_a}/100
                        </span>
                      </div>
                    </div>
                    <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative group">
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
                          Video 2: {comparisonResult.video_b.analytics?.activity_analyzed || comparisonResult.video_b.original_filename || comparisonResult.video_b.activity}
                        </span>
                        {comparisonResult.video_b.analytics?.action_auto_corrected && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            Auto-Corrected
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => playSingleVideo("B")}
                          className="px-2 py-0.5 rounded bg-pink-600/30 hover:bg-pink-600/50 text-pink-200 border border-pink-500/40 text-[10px] font-bold cursor-pointer"
                        >
                          {isPlayingB ? "Pause" : "Resume"}
                        </button>
                        <span className="text-slate-400">
                          Score: {comparisonResult.comparison.metrics_diff.risk_score.video_b}/100
                        </span>
                      </div>
                    </div>
                    <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative group">
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

          {/* Executive Biomechanical Progression & Regression Clinical Delta Report */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <h4 className="text-lg font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  Biomechanical Progression, Regression & Technique Delta Report
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Frame-by-frame analysis contrasting Video 2 (Present Trial) against Video 1 (Past Baseline).
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${comparisonResult.comparison.score_diff < 0
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                  : comparisonResult.comparison.score_diff > 0
                    ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                    : "bg-slate-700/50 text-slate-300 border border-slate-600"
                  }`}>
                  {comparisonResult.comparison.overall_verdict}
                </span>
              </div>
            </div>

            {/* 3-Column Delta Breakdown: Improvements, Deteriorations, Neutral */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* 1. Improvements & Positive Changes */}
              <div className="bg-emerald-950/20 rounded-xl p-4 border border-emerald-500/30 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wider border-b border-emerald-500/20 pb-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Verified Improvements ({comparisonResult.comparison.improvements?.length || 0})</span>
                </div>
                <div className="space-y-2.5">
                  {(comparisonResult.comparison.improvements && comparisonResult.comparison.improvements.length > 0) ? (
                    comparisonResult.comparison.improvements.map((imp, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-emerald-200/90 leading-relaxed bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-500/20">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                        <span>{imp}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-400 italic p-2 bg-slate-900/40 rounded-lg">
                      No significant kinetic improvements registered between sessions.
                    </div>
                  )}
                </div>
              </div>

              {/* 2. Deteriorations, Regressions & Declines */}
              <div className="bg-rose-950/20 rounded-xl p-4 border border-rose-500/30 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold text-rose-400 uppercase tracking-wider border-b border-rose-500/20 pb-2">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <span>Regressions & Risks ({comparisonResult.comparison.deteriorations?.length || 0})</span>
                </div>
                <div className="space-y-2.5">
                  {(comparisonResult.comparison.deteriorations && comparisonResult.comparison.deteriorations.length > 0) ? (
                    comparisonResult.comparison.deteriorations.map((det, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-rose-200/90 leading-relaxed bg-rose-950/40 p-2.5 rounded-lg border border-rose-500/20">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                        <span>{det}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-emerald-400/80 italic p-2 bg-emerald-950/30 rounded-lg border border-emerald-500/20">
                      ✓ No technical regressions or elevated injury risks identified.
                    </div>
                  )}
                </div>
              </div>

              {/* 3. Neutral & Stable Parameters */}
              <div className="bg-slate-900/40 rounded-xl p-4 border border-slate-800 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider border-b border-slate-800 pb-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span>Stable Baselines ({comparisonResult.comparison.neutral_observations?.length || 0})</span>
                </div>
                <div className="space-y-2.5">
                  {(comparisonResult.comparison.neutral_observations && comparisonResult.comparison.neutral_observations.length > 0) ? (
                    comparisonResult.comparison.neutral_observations.map((neu, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed bg-slate-950/50 p-2.5 rounded-lg border border-slate-800">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                        <span>{neu}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-500 italic p-2 bg-slate-950/30 rounded-lg">
                      Kinetic parameters evolved dynamically across trials.
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Transition & Clinical Coaching Verdict */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-2">
                  <GitBranch className="w-4 h-4 text-sky-400" />
                  Movement Demands & Action Transition
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {comparisonResult.comparison.action_transition_summary ||
                    "Movement mechanics and physical demands evaluated across baseline and present recordings."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/30 space-y-2">
                <div className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  Targeted Coaching Verdict & Prescription
                </div>
                <p className="text-xs text-indigo-200 leading-relaxed">
                  {comparisonResult.comparison.detailed_coaching_verdict ||
                    comparisonResult.video_b.analytics?.corrective_recommendation ||
                    "Focus on progressive neuromuscular control drills and unilateral balance."}
                </p>
              </div>
            </div>
          </div>

          {/* 8-Action Recognition Comparative Matrix */}
          {Array.isArray(comparisonResult.comparison.actions_comparison) && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div>
                  <h4 className="text-lg font-bold text-white flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-indigo-400" />
                    7-Action Kinetic Recognition Matrix (Video 1 vs Video 2)
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Comparative breakdown of all 7 targeted actions: Jumping, Squatting, Sprinting, Landing, Throwing, Cutting, and Drills.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-medium">
                    Automated Kinetic Classification
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                      <th className="pb-3 font-semibold">Target Athletic Action</th>
                      <th className="pb-3 font-semibold text-indigo-300">Video 1 (Baseline)</th>
                      <th className="pb-3 font-semibold text-pink-300">Video 2 (Comparison)</th>
                      <th className="pb-3 font-semibold text-center">Movement Match</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {comparisonResult.comparison.actions_comparison.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/30 transition-colors">
                        <td className="py-3.5 pr-4">
                          <div className="flex items-center gap-2.5">
                            <div className="p-1.5 rounded-lg bg-slate-800 shrink-0">
                              {ACTION_ICONS[row.action] || <Activity className="w-4 h-4 text-slate-400" />}
                            </div>
                            <span className="font-bold text-white text-sm">{row.action}</span>
                          </div>
                        </td>

                        <td className="py-3.5 pr-4">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.video_a_performed
                                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                  : "bg-slate-800 text-slate-400"
                                  }`}
                              >
                                {row.video_a_performed ? "✓ PERFORMED" : "NOT DETECTED"}
                              </span>
                              <span className="font-semibold text-slate-300">{row.video_a_confidence}%</span>
                            </div>
                            <div className="text-[10px] text-slate-400">{row.video_a_metric}</div>
                          </div>
                        </td>

                        <td className="py-3.5 pr-4">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.video_b_performed
                                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                  : "bg-slate-800 text-slate-400"
                                  }`}
                              >
                                {row.video_b_performed ? "✓ PERFORMED" : "NOT DETECTED"}
                              </span>
                              <span className="font-semibold text-slate-300">{row.video_b_confidence}%</span>
                            </div>
                            <div className="text-[10px] text-slate-400">{row.video_b_metric}</div>
                          </div>
                        </td>

                        <td className="py-3.5 text-center">
                          <span
                            className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${row.match
                              ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                              : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                              }`}
                          >
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

          {/* Full Joint Kinematics Telemetry Comparison */}
          {comparisonResult.comparison.kinematics_comparison && Object.keys(comparisonResult.comparison.kinematics_comparison).length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
              <div className="border-b border-slate-800 pb-4">
                <h4 className="text-lg font-bold text-white flex items-center gap-2">
                  <Compass className="w-5 h-5 text-indigo-400" />
                  Full Kinetic Chain Joint Angle Telemetry Comparison
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Side-by-side telemetry comparison of head tilt, trunk sway, knee valgus, elbow extension, velocities, and symmetry index.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(comparisonResult.comparison.kinematics_comparison).map(([key, data]: [string, any]) => {
                  const isPositiveImprovement = (key.includes("symmetry") && data.diff > 0) || (!key.includes("symmetry") && data.diff < 0);
                  return (
                    <div key={key} className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{data.label}</div>
                      <div className="flex items-baseline justify-between">
                        <div className="text-lg font-bold text-white">
                          <span className="text-indigo-300">{data.video_a}</span>
                          <span className="text-slate-500 mx-1.5">&rarr;</span>
                          <span className="text-pink-300">{data.video_b}</span>
                        </div>
                        <span
                          className={`text-xs font-bold px-2 py-0.5 rounded ${Math.abs(data.diff) < 0.1
                            ? "bg-slate-800 text-slate-400"
                            : isPositiveImprovement
                              ? "bg-emerald-500/20 text-emerald-400"
                              : "bg-rose-500/20 text-rose-400"
                            }`}
                        >
                          {data.diff > 0 ? "+" : ""}
                          {data.diff}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Bottom Navigation Option: Reports (Dual Video) */}
      <div className="mt-10 pt-6 border-t border-slate-800/80">
        <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 bg-slate-950/60 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
          <div className="flex items-center gap-3.5">
            <div className="p-3 bg-pink-500/10 border border-pink-500/20 rounded-xl text-pink-400 shrink-0">
              <GitCompare className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-base font-bold text-white">Dual Video Comparative Archive</h4>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-pink-500/20 text-pink-300 border border-pink-500/30">
                  Archived Reports
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 max-w-xl">
                Access all historical side-by-side comparative evaluations, 8-action kinetic recognition matrices, technique progression logs, and comparative PDF & CSV exports.
              </p>
            </div>
          </div>

          <Link
            href="/dashboard/reports-dual"
            id="btn-compare-video-reports"
            className="w-full sm:w-auto px-5 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(147,51,234,0.35)] hover:shadow-[0_0_24px_rgba(168,85,247,0.6)] border border-purple-400/30 flex items-center justify-center gap-2 shrink-0 cursor-pointer group"
          >
            <GitCompare className="w-4 h-4 text-purple-200 group-hover:text-white transition-colors" />
            <span>Reports</span>
            <span className="text-[11px] text-purple-200 font-semibold group-hover:text-white transition-colors">
              (Dual Video)
            </span>
            <ArrowRight className="w-4 h-4 text-purple-200 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
      </div>
    </div>
  );
}
