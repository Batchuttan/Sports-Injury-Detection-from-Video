"use client";

import { useState } from "react";
import Link from "next/link";
import { uploadVideo, API_URL } from "@/lib/api";

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

export default function VideoUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [activity, setActivity] = useState<string>("Auto-Detect (AI Classification)");
  const [surfaceType, setSurfaceType] = useState<string>("Unknown");
  const [footwear, setFootwear] = useState<string>("Unknown");
  const [rpe, setRpe] = useState<number>(5);
  const [sleepQuality, setSleepQuality] = useState<number>(5);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a video file first.");
      return;
    }

    setUploading(true);
    setError("");
    setResult(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authorization token found. Please log in first.");

      const targetActivity = activity.startsWith("Auto-Detect") ? "Auto-Detect" : activity;
      const response = await uploadVideo(token, file, targetActivity, surfaceType, footwear, rpe, sleepQuality);
      setResult(response);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "An error occurred during video upload and processing.";
      if (msg.includes("401") || msg.includes("credentials")) {
        setError("Your session has expired. Please log in again to continue.");
      } else {
        setError(msg);
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Video Upload & Processing Engine</h2>
          <p className="text-slate-400 text-sm mt-1">Upload athlete footage for AI-powered biomechanical analysis.</p>
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
                  AI Vision Verified
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
                AI kinematics autonomously analyzes footage to identify the true athletic action, auto-correcting any dropdown mismatch.
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
              <label className="text-sm font-medium text-slate-300">Video File</label>
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
                    {file ? file.name : "Click to browse or drag and drop"}
                  </span>
                  <span className="text-xs text-slate-500">MP4 or MOV (Max 50MB)</span>
                </label>
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-rose-500/20 border border-rose-500/50 text-rose-400 text-sm font-medium">
                {error}
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
                  Processing Engine Running...
                </>
              ) : "Process Video"}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="glass-panel p-8 rounded-2xl flex flex-col">
          <h3 className="text-lg font-bold text-white mb-6 border-b border-slate-800 pb-4">Analysis Results</h3>

          {result ? (
            <div className="space-y-6 flex-1">
              <div className="aspect-video bg-slate-950 rounded-xl overflow-hidden border border-slate-700 relative flex flex-col justify-center">
                <video
                  key={result.processed_url}
                  controls
                  autoPlay
                  muted
                  playsInline
                  preload="auto"
                  className="w-full h-full object-contain"
                  src={`${API_URL}${result.processed_url}`}
                >
                  Your browser does not support HTML5 video playback.
                </video>
                <div className={`absolute top-3 left-3 px-2 py-1 bg-black/60 backdrop-blur-md rounded border text-xs text-white flex items-center gap-2 ${result.analytics.anomaly_detected ? 'border-rose-500/50' : 'border-white/10'}`}>
                  <span className={`w-2 h-2 rounded-full ${result.analytics.anomaly_detected ? 'bg-rose-500 animate-pulse' : 'bg-green-500'}`}></span>
                  {result.analytics.anomaly_detected ? 'Anomaly Detected' : 'Motion Enhanced'}
                </div>
                <div className="absolute top-3 right-3">
                  <a
                    href={`${API_URL}${result.processed_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-2.5 py-1 bg-slate-900/80 hover:bg-slate-800 text-xs text-indigo-300 hover:text-white rounded border border-indigo-500/30 backdrop-blur-md transition-colors"
                  >
                    Open Raw ↗
                  </a>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-1">
                  <div className="text-xs text-slate-500 uppercase font-semibold flex items-center justify-between">
                    <span>Activity Analyzed</span>
                    {result.analytics?.action_auto_corrected && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium">
                        Auto-Corrected
                      </span>
                    )}
                  </div>
                  <div className="text-lg font-bold text-white">{result.analytics.activity_analyzed}</div>
                  {result.analytics?.action_auto_corrected && result.analytics?.user_input_activity && (
                    <div className="text-[11px] text-amber-400/90 font-medium pt-0.5">
                      Input: &ldquo;{result.analytics.user_input_activity}&rdquo; &rarr; AI classified &ldquo;{result.analytics.activity_analyzed}&rdquo;
                    </div>
                  )}
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Risk Score</div>
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
                        <svg className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
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
              <p>Upload a video to see frame extraction, <br />motion enhancement, and risk detection results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
