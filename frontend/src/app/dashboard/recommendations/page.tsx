"use client";

import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { getActivityRecommendations, getAnalyses } from "@/lib/api";
import {
  ShieldAlert,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  Flame,
  Zap,
  Target,
  ArrowLeft,
  ChevronRight,
  PlayCircle
} from "lucide-react";

const SUPPORTED_ACTIVITIES = [
  "Throwing",
  "Squatting",
  "Sprinting",
  "Jumping / Landing",
  "Cutting Movements",
  "Sports Specific Drills"
];

function RecommendationsContent() {
  const searchParams = useSearchParams();
  const initialActivity = searchParams.get("activity") || "Throwing";
  const initialRisk = searchParams.get("risk") || "High Risk";

  const [selectedActivity, setSelectedActivity] = useState<string>(initialActivity);
  const [riskLevel, setRiskLevel] = useState<string>(initialRisk);
  const [recData, setRecData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const act = searchParams.get("activity");
    if (act) {
      setSelectedActivity(act);
    }
    const rsk = searchParams.get("risk");
    if (rsk) {
      setRiskLevel(rsk);
    }
  }, [searchParams]);

  useEffect(() => {
    let isMounted = true;
    const fetchRec = async () => {
      try {
        setLoading(true);
        setError("");
        const token = localStorage.getItem("token");
        if (!token) return;

        const data = await getActivityRecommendations(token, selectedActivity, riskLevel);
        if (isMounted) {
          setRecData(data);
        }
      } catch (err: any) {
        console.error("Failed to load recommendations:", err);
        if (isMounted) setError(err.message || "Failed to load clinical recommendations");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchRec();
    return () => {
      isMounted = false;
    };
  }, [selectedActivity, riskLevel]);

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16 animate-fadeIn">
      {/* Top Breadcrumb & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <Link href="/dashboard" className="hover:text-indigo-400 transition-colors flex items-center gap-1">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Dashboard</span>
            </Link>
            <ChevronRight className="w-3 h-3 text-slate-600" />
            <Link href="/dashboard/reports" className="hover:text-indigo-400 transition-colors">
              Reports
            </Link>
            <ChevronRight className="w-3 h-3 text-slate-600" />
            <span className="text-indigo-400 font-medium">Corrective Recommendations</span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <ShieldAlert className="w-7 h-7 text-rose-400 shrink-0" />
            <span>Clinical Corrective & Biomechanical Recommendations</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Targeted neuromuscular prescriptions and joint-sparing form cues tailored to identified movement risks.
          </p>
        </div>

        <Link
          href={`/dashboard/training?plan=${recData?.training_plan_ref || "knee-valgus"}`}
          className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] shrink-0"
        >
          <span>Open Prescribed Training Plan</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Activity Selector Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider shrink-0 mr-1">Activity:</span>
        {SUPPORTED_ACTIVITIES.map((act) => {
          const isSelected = selectedActivity.toLowerCase().includes(act.toLowerCase().split(" ")[0]);
          return (
            <button
              key={act}
              type="button"
              onClick={() => setSelectedActivity(act)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${isSelected
                ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)] border border-indigo-400/40"
                : "bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800"
                }`}
            >
              {act}
            </button>
          );
        })}
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="glass-panel p-16 rounded-3xl border border-slate-800 text-center flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-slate-400">Loading tailored clinical recommendations for {selectedActivity}...</span>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      ) : recData ? (
        <div className="space-y-6">
          {/* Risk Alert Banner */}
          <div className="p-5 rounded-2xl bg-gradient-to-r from-rose-950/40 via-slate-900/80 to-slate-900/60 border border-rose-500/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[11px] font-extrabold uppercase tracking-wider">
                  {riskLevel} Detected
                </span>
                <span className="text-xs text-slate-400">• Dynamic Video Pose Assessment</span>
              </div>
              <h3 className="text-lg font-bold text-white">
                Biomechanical Vulnerability Flagged in: <span className="text-rose-300">{recData.activity}</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
                {recData.clinical_rationale}
              </p>
            </div>

            <div className="shrink-0 p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-500 block uppercase font-bold tracking-wider">Primary Risk Vector</span>
              <strong className="text-rose-400 text-sm">
                {recData.activity === "Throwing" ? "Medial Elbow / Shoulder" : recData.activity === "Squatting" ? "Dynamic Knee Valgus (ACL)" : "High Kinetic Shear"}
              </strong>
            </div>
          </div>

          {/* Primary Biomechanical Risk Factors */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <Flame className="w-5 h-5 text-amber-400" />
              <span>Identified Biomechanical Risk Factors & Joint Shear Vectors</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {recData.primary_risk_factors?.map((rf: string, idx: number) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                  <div className="w-6 h-6 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center font-bold text-xs border border-rose-500/20">
                    {idx + 1}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {rf}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Actionable Form Cues */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span>Real-Time Kinetic Coaching Cues & Motor Re-Education</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {recData.corrective_cues?.map((cue: string, idx: number) => (
                <div key={idx} className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/20 space-y-2 flex flex-col justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider">Form Cue #{idx + 1}</span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-medium">
                    &ldquo;{cue}&rdquo;
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Prescribed Corrective Exercises */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-sm font-bold text-white">
                <Zap className="w-5 h-5 text-pink-400" />
                <span>Prescribed Corrective Neuromuscular Exercises</span>
              </div>
              <span className="text-xs text-slate-400">
                Frequency: 3-4x / week • Pre-training or rehabilitation block
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {recData.prescribed_exercises?.map((ex: any, idx: number) => (
                <div key={idx} className="bg-slate-900/70 p-4 rounded-2xl border border-slate-800 space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex justify-between items-start gap-2">
                      <h4 className="font-bold text-white text-sm">{ex.name}</h4>
                      <span className="text-[10px] font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 shrink-0">
                        {ex.tempo}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-300">
                      <div>
                        <span className="text-slate-500 block text-[10px]">Sets</span>
                        <strong>{ex.sets}</strong>
                      </div>
                      <div className="w-px h-6 bg-slate-800" />
                      <div>
                        <span className="text-slate-500 block text-[10px]">Reps</span>
                        <strong>{ex.reps}</strong>
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 leading-relaxed pt-1">
                      {ex.notes}
                    </p>
                  </div>

                  <Link
                    href={`/dashboard/training?plan=${recData.training_plan_ref || "knee-valgus"}`}
                    className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition-colors cursor-pointer border border-slate-700/80"
                  >
                    <PlayCircle className="w-3.5 h-3.5" />
                    <span>View in Training Plan</span>
                  </Link>
                </div>
              ))}
            </div>
          </div>

          {/* Recovery & Regeneration Protocol */}
          {recData.recovery_protocol && (
            <div className="p-5 rounded-2xl bg-teal-950/20 border border-teal-500/30 space-y-2">
              <div className="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-2">
                <Target className="w-4 h-4 text-teal-400" />
                <span>Immediate Post-Session Recovery & Regeneration Protocol</span>
              </div>
              <p className="text-xs text-teal-200/90 leading-relaxed">
                {recData.recovery_protocol}
              </p>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

export default function RecommendationsPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-slate-400">Loading recommendations...</div>}>
      <RecommendationsContent />
    </Suspense>
  );
}
