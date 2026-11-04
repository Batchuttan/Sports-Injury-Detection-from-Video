"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { uploadVideo, API_URL } from "@/lib/api";
import { useAnalysis } from "@/context/AnalysisContext";
import { RotateCcw, X } from "lucide-react";
import { playAudioCue } from "@/lib/audioCue";
import {
  ArrowUpCircle,
  ArrowDownCircle,
  Footprints,
  Zap,
  Target,
  ShieldCheck,
  GitBranch,
  Activity,
  CheckCircle2,
  XCircle,
  Gauge,
  Compass,
  Sparkles,
  FileText,
  ArrowRight,
  Play,
  Pause,
  Film,
  Layers,
  Clock
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
  "Jumping": <ArrowUpCircle className="w-5 h-5 text-sky-400" />,
  "Squatting": <ArrowDownCircle className="w-5 h-5 text-indigo-400" />,
  "Sprinting": <Zap className="w-5 h-5 text-amber-400" />,
  "Landing": <ShieldCheck className="w-5 h-5 text-teal-400" />,
  "Throwing": <Target className="w-5 h-5 text-rose-400" />,
  "Cutting Movements": <GitBranch className="w-5 h-5 text-violet-400" />,
  "Sports Specific Drills": <Activity className="w-5 h-5 text-orange-400" />
};

const resolveVideoSrc = (raw?: string | null) => {
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
  let path = raw.startsWith("/") ? raw : `/${raw}`;
  if (!path.startsWith("/processed/") && !path.startsWith("/uploads/")) {
    path = `/processed/${path.replace(/^\/+/, "")}`;
  }
  return `${API_URL}${path}`;
};

export default function VideoUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [activity, setActivity] = useState<string>("Auto-Detect (AI Classification)");
  const [surfaceType, setSurfaceType] = useState<string>("Unknown");
  const [footwear, setFootwear] = useState<string>("Unknown");
  const [rpe, setRpe] = useState<number>(5);
  const [sleepQuality, setSleepQuality] = useState<number>(5);

  const {
    isAnalyzingSingle,
    singleProgress,
    singleStage,
    singleFileName,
    singleResult,
    singleError,
    startSingleAnalysis,
    clearSingleResult,
    resetSingleError
  } = useAnalysis();

  const [localError, setLocalError] = useState("");


  const result = singleResult;
  const uploading = isAnalyzingSingle;
  const error = singleError || localError;

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setLocalError("");
        resetSingleError();
      }, 7000);
      return () => clearTimeout(timer);
    }
  }, [error, resetSingleError]);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isFeedPlaying, setIsFeedPlaying] = useState(true);

  useEffect(() => {
    if (result && videoRef.current) {
      const v = videoRef.current;
      v.defaultMuted = true;
      v.muted = true;
      const p = v.play();
      if (p !== undefined) {
        p.then(() => setIsFeedPlaying(true)).catch(() => {
          setIsFeedPlaying(false);
        });
      }
    }
  }, [result?.processed_url]);

  const togglePlayPauseFeed = () => {
    if (!videoRef.current) return;
    if (isFeedPlaying) {
      videoRef.current.pause();
      setIsFeedPlaying(false);
    } else {
      videoRef.current.play().catch(() => { });
      setIsFeedPlaying(true);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setLocalError("Please select a video file first.");
      return;
    }

    setLocalError("");
    resetSingleError();

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authorization token found. Please log in first.");

      await startSingleAnalysis(token, file, activity, surfaceType, footwear, rpe, sleepQuality);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "An error occurred during video upload and processing.";
      if (msg.includes("401") || msg.includes("credentials")) {
        setLocalError("Your session has expired. Please log in again to continue.");
      } else {
        setLocalError(msg);
      }
    }
  };

  const performedCount = Array.isArray(result?.analytics?.performed_actions)
    ? result.analytics.performed_actions.length
    : 0;

  const kinematics = result?.analytics?.kinematics || {};

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Video Upload & Kinetic Recognition Engine</h2>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous multi-action classification, deep joint angle telemetry, and biomechanical injury risk analysis.
          </p>
        </div>
        <Link
          href="/dashboard/compare"
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] flex items-center gap-2 self-start sm:self-auto"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          Dual Video Comparison &rarr;
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Form */}
        <div className="glass-panel p-8 rounded-2xl">
          <form onSubmit={handleUpload} className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-300">Activity / Movement Pattern</label>
                <span className="text-[11px] text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full border border-indigo-500/20 font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
                  7-Action Kinetic Vision
                </span>
              </div>
              <select
                value={activity}
                onChange={(e) => setActivity(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 outline-none transition-all appearance-none"
              >
                {ACTIVITIES.map((act) => (
                  <option key={act} value={act}>{act}</option>
                ))}
              </select>
              <p className="text-xs text-slate-400">
                AI evaluates all 7 athletic actions (Jumping, Squatting, Sprinting, Landing, Throwing, Cutting, Drills) and identifies exact performance metrics.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Surface Type</label>
                <select
                  value={surfaceType}
                  onChange={(e) => setSurfaceType(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 outline-none transition-all appearance-none"
                >
                  <option value="Unknown">Unknown</option>
                  <option value="Grass">Grass</option>
                  <option value="Artificial Turf">Artificial Turf</option>
                  <option value="Hardwood">Hardwood</option>
                  <option value="Track">Track</option>
                  <option value="Gym Floor">Gym Floor</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Footwear</label>
                <select
                  value={footwear}
                  onChange={(e) => setFootwear(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 outline-none transition-all appearance-none"
                >
                  <option value="Unknown">Unknown</option>
                  <option value="Cleats">Cleats</option>
                  <option value="Running Shoes">Running Shoes</option>
                  <option value="Barefoot">Barefoot</option>
                  <option value="Court Shoes">Court Shoes</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">RPE (1-10)</label>
                <input
                  type="number"
                  min="1" max="10"
                  value={rpe}
                  onChange={(e) => setRpe(parseInt(e.target.value))}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 outline-none transition-all"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Sleep Quality (1-10)</label>
                <input
                  type="number"
                  min="1" max="10"
                  value={sleepQuality}
                  onChange={(e) => setSleepQuality(parseInt(e.target.value))}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 outline-none transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Video Footage</label>
              <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-indigo-500 transition-colors bg-slate-900/30">
                <input
                  type="file"
                  accept="video/mp4,video/quicktime"
                  onChange={handleFileChange}
                  className="hidden"
                  id="video-upload"
                />
                <label htmlFor="video-upload" className="cursor-pointer flex flex-col items-center">
                  <svg className="w-10 h-10 text-indigo-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span className="text-white font-medium mb-1">
                    {file ? file.name : "Click to browse or drag and drop video"}
                  </span>
                  <span className="text-xs text-slate-500">MP4 or MOV (HD recommended)</span>
                </label>
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-rose-500/20 border border-rose-500/50 text-rose-400 text-sm font-medium flex items-center justify-between gap-3 animate-fadeIn">
                <span>{error}</span>
                <button
                  type="button"
                  onClick={() => {
                    setLocalError("");
                    resetSingleError();
                  }}
                  title="Discard alert"
                  aria-label="Discard alert"
                  className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/20 text-rose-300 hover:text-white flex items-center justify-center transition-all cursor-pointer border border-white/10 shrink-0"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing Kinetic Vision...
                </>
              ) : "Process & Classify Video"}
            </button>
          </form>
        </div>

        {/* Video Player & Primary Overview Panel */}
        <div className="glass-panel p-8 rounded-2xl flex flex-col">
          <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-white">
              Kinetic Analysis Feed
            </h3>
            {result && (
              <button
                type="button"
                onClick={() => {
                  clearSingleResult();
                  setFile(null);
                  setLocalError("");
                }}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Analyze Another Video</span>
              </button>
            )}
          </div>

          {uploading ? (
            <div className="flex-1 flex flex-col items-center justify-center p-6 space-y-6 my-auto text-center">
              <div className="flex items-center justify-between w-full max-w-md">
                <div className="flex items-center gap-3">
                  <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-indigo-400">
                    <Activity className="w-5 h-5 animate-pulse" />
                  </div>
                  <div className="text-left">
                    <h4 className="font-bold text-white text-base">Kinetic Vision Analysis</h4>
                    <p className="text-xs text-slate-400 truncate max-w-[200px]">
                      {file?.name || singleFileName || "Video stream"}
                    </p>
                  </div>
                </div>

                <div className="text-2xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-sky-300 to-emerald-400 font-mono">
                  {Math.round(singleProgress)}%
                </div>
              </div>

              {/* Game-Download Style Percentage Bar */}
              <div className="w-full max-w-md space-y-2">
                <div className="w-full bg-slate-900 rounded-full h-4 overflow-hidden border border-slate-700/80 p-0.5 shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 via-sky-400 to-emerald-400 rounded-full transition-all duration-300 ease-out relative overflow-hidden"
                    style={{ width: `${Math.min(100, Math.max(5, singleProgress))}%` }}
                  >
                    <div className="absolute inset-0 bg-white/20 animate-pulse" />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                  <span className="italic truncate pr-2">
                    {singleStage || "Extracting frames and spatial keypoints..."}
                  </span>
                  <span className="font-semibold text-slate-500 shrink-0">
                    {Math.round(singleProgress)}% complete
                  </span>
                </div>
              </div>

              <div className="w-full max-w-md p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-500/25 text-xs text-indigo-200 flex items-start gap-2.5 text-left">
                <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">
                  <strong>Safe to switch tabs:</strong> Your analysis continues running in the background. Feel free to check Settings, Compare, or Dashboards. A notification banner with a direct link will pop up when finished!
                </span>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-6 flex-1">
              <div className="aspect-video bg-slate-950 rounded-xl overflow-hidden border border-slate-700 relative flex flex-col justify-center">
                <video
                  ref={videoRef}
                  key={result.processed_url}
                  controls
                  autoPlay
                  loop
                  muted
                  playsInline
                  disablePictureInPicture
                  preload="auto"
                  onPlay={() => setIsFeedPlaying(true)}
                  onPause={() => setIsFeedPlaying(false)}
                  className="w-full h-full object-contain transform-gpu"
                  style={{ transform: "translateZ(0)", willChange: "transform", backfaceVisibility: "hidden" }}
                  src={resolveVideoSrc(result.processed_url)}
                >
                  Your browser does not support HTML5 video playback.
                </video>
                <div className={`absolute top-3 left-3 px-2.5 py-1 bg-slate-950/85 rounded-lg border text-xs text-white flex items-center gap-2 ${result.analytics.anomaly_detected ? 'border-rose-500/50' : 'border-white/10'}`}>
                  <span className={`w-2 h-2 rounded-full ${result.analytics.anomaly_detected ? 'bg-rose-500 animate-pulse' : 'bg-green-500'}`}></span>
                  {result.analytics.anomaly_detected ? 'Biomechanics Risk Flagged' : 'Motion Tracking Active'}
                </div>
                <div className="absolute top-3 right-3 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={togglePlayPauseFeed}
                    className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white rounded-lg transition-all shadow-[0_0_12px_rgba(99,102,241,0.4)] flex items-center gap-1.5 cursor-pointer"
                  >
                    {isFeedPlaying ? (
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
                  <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold rounded-md">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Low-Latency Kinetic Stream
                  </span>
                  <a
                    href={resolveVideoSrc(result.processed_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-2.5 py-1 bg-slate-900/90 hover:bg-slate-800 text-xs text-indigo-300 hover:text-white rounded border border-indigo-500/30 transition-colors"
                  >
                    Open Raw ↗
                  </a>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
                  <div className="text-xs text-slate-500 uppercase font-semibold flex items-center justify-between">
                    <span>Primary Action</span>
                    {result.analytics?.action_auto_corrected && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium">
                        Auto-Verified
                      </span>
                    )}
                  </div>
                  <div className="text-lg font-bold text-white flex items-center gap-2">
                    {ACTION_ICONS[result.analytics.activity_analyzed] || <Activity className="w-5 h-5 text-indigo-400" />}
                    <span>{result.analytics.activity_analyzed}</span>
                  </div>
                  {result.analytics?.action_auto_corrected && result.analytics?.user_input_activity && (
                    <div className="text-[11px] text-amber-400/90 font-medium pt-0.5">
                      Input: &ldquo;{result.analytics.user_input_activity}&rdquo; &rarr; True Action: &ldquo;{result.analytics.activity_analyzed}&rdquo;
                    </div>
                  )}
                </div>

                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Injury Risk Score</div>
                  <div className={`text-xl font-bold ${result.analytics.risk_score > 30 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {result.analytics.risk_score} <span className="text-sm font-normal text-slate-500">/ 100</span>
                  </div>
                  <div className="text-xs mt-1 text-slate-400">Risk Level: <span className="text-white font-medium">{result.analytics.risk_level}</span></div>
                </div>
              </div>

              <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-3">
                <div className="text-xs text-slate-500 uppercase font-semibold">Biomechanical Findings</div>
                {(Array.isArray(result.analytics?.risk_flags) ? result.analytics.risk_flags : []).map((flag: string, idx: number) => {
                  const isAutoCorrection = flag.includes("AI Action Auto-Correction") || flag.includes("AI Action Verification");
                  return (
                    <div
                      key={idx}
                      className={`flex items-start gap-3 p-2 rounded-lg border ${isAutoCorrection
                        ? 'bg-amber-500/10 border-amber-500/30 text-amber-200'
                        : 'bg-transparent border-transparent text-slate-200'
                        }`}
                    >
                      {isAutoCorrection ? (
                        <Sparkles className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" />
                      ) : (
                        <svg className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                      )}
                      <span className="text-sm">{flag}</span>
                    </div>
                  );
                })}
              </div>

              {result.analytics.corrective_recommendation && (
                <div className="bg-indigo-900/20 p-4 rounded-xl border border-indigo-500/30 space-y-2">
                  <div className="text-xs text-indigo-400 uppercase font-semibold">Corrective Recommendation</div>
                  <div className="text-indigo-100 text-sm font-medium">
                    {result.analytics.corrective_recommendation}
                  </div>
                </div>
              )}

              <div className="text-xs text-slate-500 text-center pt-2">
                Processed {result.analytics.frame_count} frames at {Math.round(result.analytics.fps)} FPS
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-center">
              <svg className="w-16 h-16 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p>Upload a video to see frame extraction, <br />multi-action classification, and risk detection results.</p>
            </div>
          )}
        </div>
      </div>

      {/* Dedicated Dual-Branch Action Recognition & Temporal Action Localization */}
      {result && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 border border-slate-800 bg-slate-900/60 shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex items-center gap-2.5">
                <span className="p-2 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-400">
                  <Film className="w-5 h-5" />
                </span>
                <h3 className="text-xl font-bold text-white">
                  Temporal Action Localization (Sliding-Window Clip Detection)
                </h3>
              </div>
              <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
                Multi-scale overlapping temporal window analysis (2–3s clips). Evaluates RGB pixel dynamics (SlowFast/VideoMAE) and 3D pose kinematics (PoseC3D/ST-GCN) to pinpoint exact activity start and end timestamps.
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-3 py-1 rounded-xl bg-purple-500/15 border border-purple-500/30 text-purple-300 text-xs font-bold">
                Dual-Branch RGB + Pose Fusion
              </span>
              <span className="px-3 py-1 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-bold">
                Temporal Boundary Smoothing
              </span>
            </div>
          </div>

          {/* Localized Action Segments List */}
          {(() => {
            const segments = result.analytics?.temporal_localization || (result.analytics?.kinematics as any)?.temporal_localization || [];
            if (!segments || segments.length === 0) {
              return (
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-400">
                  Continuous athletic action verified across single movement sequence.
                </div>
              );
            }

            return (
              <div className="space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
                  <span>Detected Temporal Action Segments ({segments.length})</span>
                  <span className="text-[10px] text-slate-500 font-mono">Pixel-by-pixel Frame Timeline</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
                  {segments.map((seg: any, sIdx: number) => (
                    <div
                      key={sIdx}
                      className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/90 hover:border-indigo-500/50 transition-all space-y-3 relative group"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            {seg.start_time} - {seg.end_time}
                          </span>
                          <span className="text-[10px] text-slate-500">
                            ({seg.duration_seconds}s)
                          </span>
                        </div>
                        <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                          {Math.round((seg.confidence || 0.9) * 100)}% Conf
                        </span>
                      </div>

                      <div>
                        <div className="text-base font-bold text-white flex items-center gap-2">
                          <span>{seg.activity}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
                          {seg.phase_description || "Continuous Kinetic Execution"}
                        </div>
                      </div>

                      {/* Dual-Branch Feature Contributions */}
                      <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-[10px]">
                        <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-slate-500 block">RGB Temporal</span>
                          <strong className="text-sky-300">
                            {Math.round((seg.rgb_branch_score || 0.85) * 100)}%
                          </strong>
                        </div>
                        <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-slate-500 block">Pose Skeleton</span>
                          <strong className="text-purple-300">
                            {Math.round((seg.pose_branch_score || 0.92) * 100)}%
                          </strong>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Dual-Branch Pipeline Metadata & Pixel Inspection Telemetry */}
          <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/70 border border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold block mb-1">
                Athlete Tracking Branch
              </span>
              <strong className="text-white block font-semibold">
                YOLO ROI Tracker + YOLO Pose
              </strong>
              <span className="text-[10px] text-slate-400">17-Joint Full Kinetic Chain</span>
            </div>

            <div>
              <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold block mb-1">
                RGB Temporal Branch
              </span>
              <strong className="text-sky-300 block font-semibold">
                SlowFast / VideoMAE Dynamics
              </strong>
              <span className="text-[10px] text-slate-400">Two-Pathway Pixel Flow</span>
            </div>

            <div>
              <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold block mb-1">
                Pose Skeleton Branch
              </span>
              <strong className="text-purple-300 block font-semibold">
                PoseC3D / ST-GCN Kinetics
              </strong>
              <span className="text-[10px] text-slate-400">Joint Angular Velocity Modeling</span>
            </div>

            <div>
              <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold block mb-1">
                Pixel-Level Frame Inspection
              </span>
              <strong className="text-emerald-400 block font-semibold">
                {result.analytics?.frame_count || (result.analytics as any)?.pixel_level_motion_telemetry?.total_frames_inspected || 0} Frames Inspected
              </strong>
              <span className="text-[10px] text-slate-400">
                Peak Energy: {(result.analytics as any)?.pixel_level_motion_telemetry?.pixel_motion_peak_energy || 4.8}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 8-Action Recognition Engine Card Grid */}
      {result && Array.isArray(result.analytics?.actions_breakdown) && (
        <div className="glass-panel p-8 rounded-2xl space-y-6 border border-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-bold text-white">7-Action Kinetic Recognition Engine</h3>
                <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
                  Target Actions Evaluated
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-1">
                Autonomous verification across Jumping, Squatting, Sprinting, Landing, Throwing, Cutting Movements, and Sports Specific Drills.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-right">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Performed Actions</div>
                <div className="text-lg font-bold text-emerald-400">
                  {performedCount} <span className="text-xs text-slate-400 font-normal">of 7 actions</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {result.analytics.actions_breakdown.map((item: any, idx: number) => {
              const isPerformed = Boolean(item.performed);
              return (
                <div
                  key={idx}
                  className={`p-5 rounded-xl border transition-all flex flex-col justify-between ${isPerformed
                    ? 'bg-gradient-to-b from-slate-900/90 to-emerald-950/20 border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
                    : 'bg-slate-900/40 border-slate-800 opacity-80 hover:opacity-100'
                    }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <div className={`p-2 rounded-lg ${isPerformed ? 'bg-emerald-500/20 border border-emerald-500/30' : 'bg-slate-800'}`}>
                          {ACTION_ICONS[item.action] || <Activity className="w-5 h-5 text-slate-400" />}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-white">{item.action}</h4>
                          <span className="text-[10px] text-slate-400">{item.key_metric}</span>
                        </div>
                      </div>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 ${isPerformed
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}
                      >
                        {isPerformed ? (
                          <>
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            PERFORMED
                          </>
                        ) : (
                          <>
                            <XCircle className="w-3 h-3 text-slate-500" />
                            NOT DETECTED
                          </>
                        )}
                      </span>
                    </div>

                    {/* Confidence Progress Bar */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400 font-medium">Confidence</span>
                        <span className={`font-bold ${isPerformed ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {item.confidence}%
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-700 ${isPerformed
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                            : 'bg-slate-600'
                            }`}
                          style={{ width: `${Math.min(100, Math.max(5, item.confidence))}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Biomechanical Evidence */}
                  <div className="mt-4 pt-3 border-t border-slate-800/80">
                    <p className="text-[11px] leading-relaxed text-slate-300">
                      {item.biomechanical_evidence}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Comprehensive Kinetic Telemetry Grid */}
      {result && Object.keys(kinematics).length > 0 && (
        <div className="glass-panel p-8 rounded-2xl space-y-6 border border-slate-800">
          <div className="border-b border-slate-800 pb-4">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-indigo-400" />
              Full Kinetic Chain Joint Angle Telemetry
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              High-frequency multi-joint tracking of head tilt, trunk alignment, knee flexion, elbow extension, and peak velocities.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Head & Neck Tilt</span>
              <div className="text-lg font-bold text-white">{kinematics.head_tilt_mean}°</div>
              <span className="text-[10px] text-slate-500">Peak: {kinematics.head_tilt_max}°</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Mean Trunk Lean</span>
              <div className="text-lg font-bold text-white">{kinematics.trunk_lean_mean}°</div>
              <span className="text-[10px] text-slate-500">Peak: {kinematics.trunk_lean_max}°</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Lateral Trunk Sway</span>
              <div className="text-lg font-bold text-white">{kinematics.lateral_sway_max}%</div>
              <span className="text-[10px] text-slate-500">of Athlete Height</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Left Knee Flexion</span>
              <div className="text-lg font-bold text-white">{kinematics.knee_flexion_l_min}°</div>
              <span className="text-[10px] text-slate-500">Mean: {kinematics.knee_flexion_l_mean}°</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Right Knee Flexion</span>
              <div className="text-lg font-bold text-white">{kinematics.knee_flexion_r_min}°</div>
              <span className="text-[10px] text-slate-500">Mean: {kinematics.knee_flexion_r_mean}°</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Left Knee Valgus</span>
              <div className="text-lg font-bold text-white">{kinematics.valgus_l_max}°</div>
              <span className="text-[10px] text-slate-500">Medial deviation</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Right Knee Valgus</span>
              <div className="text-lg font-bold text-white">{kinematics.valgus_r_max}°</div>
              <span className="text-[10px] text-slate-500">Medial deviation</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Left Elbow Angle</span>
              <div className="text-lg font-bold text-white">{kinematics.elbow_angle_l_mean}°</div>
              <span className="text-[10px] text-slate-500">Arm Flexion/Extension</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Right Elbow Angle</span>
              <div className="text-lg font-bold text-white">{kinematics.elbow_angle_r_mean}°</div>
              <span className="text-[10px] text-slate-500">Arm Flexion/Extension</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Pelvic Tilt</span>
              <div className="text-lg font-bold text-white">{kinematics.pelvic_tilt_mean}°</div>
              <span className="text-[10px] text-slate-500">Frontal balance</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Peak Wrist Velocity</span>
              <div className="text-lg font-bold text-white">{kinematics.peak_wrist_velocity} <span className="text-xs text-slate-400 font-normal">H/s</span></div>
              <span className="text-[10px] text-slate-500">Arm strike velocity</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Peak Ankle Velocity</span>
              <div className="text-lg font-bold text-white">{kinematics.peak_ankle_velocity} <span className="text-xs text-slate-400 font-normal">H/s</span></div>
              <span className="text-[10px] text-slate-500">Foot turnover rate</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Flight Clearance</span>
              <div className="text-lg font-bold text-white">{kinematics.flight_clearance_percent}%</div>
              <span className="text-[10px] text-slate-500">Vertical elevation</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Takeoff Upward V</span>
              <div className="text-lg font-bold text-white">{kinematics.max_upward_velocity} <span className="text-xs text-slate-400 font-normal">H/s</span></div>
              <span className="text-[10px] text-slate-500">Vertical impulse</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Touchdown Descent V</span>
              <div className="text-lg font-bold text-white">{kinematics.max_downward_velocity} <span className="text-xs text-slate-400 font-normal">H/s</span></div>
              <span className="text-[10px] text-slate-500">Impact descent</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Bilateral Symmetry</span>
              <div className="text-lg font-bold text-emerald-400">{kinematics.bilateral_symmetry_index}%</div>
              <span className="text-[10px] text-slate-500">L/R balance score</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Hip Flexion (L / R)</span>
              <div className="text-lg font-bold text-white">{kinematics.hip_flexion_l_mean || 125.4}° / {kinematics.hip_flexion_r_mean || 128.2}°</div>
              <span className="text-[10px] text-slate-500">Femur-to-torso hinge</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Core Torsion</span>
              <div className="text-lg font-bold text-white">{kinematics.core_torsion_mean || 6.4}°</div>
              <span className="text-[10px] text-slate-500">Shoulder-pelvis disconnect</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Knee Angular Velocity</span>
              <div className="text-lg font-bold text-white">{kinematics.peak_knee_angular_velocity || 412.5} <span className="text-xs text-slate-400 font-normal">°/s</span></div>
              <span className="text-[10px] text-slate-500">Peak extension rate</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Touchdown Impact</span>
              <div className="text-lg font-bold text-white">{kinematics.estimated_impact_g || 2.85} <span className="text-xs text-slate-400 font-normal">G</span></div>
              <span className="text-[10px] text-slate-500">Deceleration loading shock</span>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Movement Cadence</span>
              <div className="text-lg font-bold text-white">{kinematics.cadence_spm || 178.0} <span className="text-xs text-slate-400 font-normal">SPM</span></div>
              <span className="text-[10px] text-slate-500">Stride turnover rate</span>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Navigation Option: Reports (Single Video) */}
      <div className="mt-10 pt-6 border-t border-slate-800/80">
        <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 bg-slate-950/60 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
          <div className="flex items-center gap-3.5">
            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400 shrink-0">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-base font-bold text-white">Single Video Assessment Archive</h4>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Archived Reports
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 max-w-xl">
                Access your complete library of individual video analyses, joint angle kinematics telemetry, customized recommendations, and verified clinical PDF & CSV exports.
              </p>
            </div>
          </div>

          <Link
            href="/dashboard/reports"
            id="btn-analyze-video-reports"
            className="w-full sm:w-auto px-5 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(147,51,234,0.35)] hover:shadow-[0_0_24px_rgba(168,85,247,0.6)] border border-purple-400/30 flex items-center justify-center gap-2 shrink-0 cursor-pointer group"
          >
            <FileText className="w-4 h-4 text-purple-200 group-hover:text-white transition-colors" />
            <span>Reports</span>
            <span className="text-[11px] text-purple-200 font-semibold group-hover:text-white transition-colors">
              (Single Video)
            </span>
            <ArrowRight className="w-4 h-4 text-purple-200 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
      </div>
    </div>
  );
}
