"use client";

import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  getTrainingPlans,
  getTrainingPlanDetail,
  toggleTrainingPlanTask,
  updateTrainingPlan,
  reactivateTrainingPlan
} from "@/lib/api";
import {
  Award,
  CheckCircle2,
  Clock,
  Target,
  Sparkles,
  RotateCcw,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
  Flame,
  Zap,
  Activity,
  CheckCheck,
  ChevronRight,
  PlayCircle,
  X
} from "lucide-react";

interface PlanSummary {
  id: number;
  plan_id: string;
  title: string;
  duration: string;
  status: string;
  focus: string;
  target_joint: string;
  tasks: string[];
  progress_percent: number;
  description: string;
}

interface ExerciseDetail {
  name: string;
  alias?: string;
  target_muscles?: string[];
  frequency?: string;
  sets?: number;
  reps?: string;
  rest?: string;
  tempo?: string;
  completed?: boolean;
  biomechanical_rationale?: string;
  form_cues?: string[];
}

interface SchedulePhase {
  week?: string;
  phase?: string;
  objective: string;
  intensity: string;
}

interface FullPlanDetail {
  id: number;
  plan_id: string;
  title: string;
  duration: string;
  status: string;
  focus: string;
  target_joint: string;
  description: string;
  prescribed_exercises: string[];
  exercises_detail: ExerciseDetail[];
  weekly_schedule: SchedulePhase[];
  clinical_notes?: string;
  progress_percent: number;
  updated_at?: string;
}

function TrainingPlansContent() {
  const searchParams = useSearchParams();
  const planParam = searchParams.get("plan");

  const [allPlans, setAllPlans] = useState<PlanSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState<FullPlanDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [actionSuccess, setActionSuccess] = useState("");
  const [activeTab, setActiveTab] = useState<"active" | "completed" | "all">("active");
  const [searchQuery, setSearchQuery] = useState("");

  const loadPlans = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      // Fetch all plans from backend to calculate active vs completed counts
      const data = await getTrainingPlans(token, true, "all");
      setAllPlans(data || []);
    } catch (err) {
      console.error("Failed to load training plans:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlans();
  }, []);

  // Auto-open requested plan from query parameter if present
  useEffect(() => {
    if (planParam && !selectedPlan) {
      handleOpenPlanDetails(planParam);
    }
  }, [planParam]);

  const handleOpenPlanDetails = async (planId: string) => {
    setLoadingDetail(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token found");
      const details = await getTrainingPlanDetail(token, planId);
      setSelectedPlan(details);
    } catch (err) {
      console.error("Failed to fetch plan detail:", err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleToggleTask = async (exerciseName: string, currentCompleted: boolean) => {
    if (!selectedPlan) return;
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const nextVal = !currentCompleted;
      const res = await toggleTrainingPlanTask(token, selectedPlan.plan_id, exerciseName, nextVal);

      // Update modal state
      setSelectedPlan(prev => {
        if (!prev) return null;
        const updatedList = prev.exercises_detail.map(ex =>
          ex.name.toLowerCase() === exerciseName.toLowerCase() ? { ...ex, completed: nextVal } : ex
        );
        return {
          ...prev,
          status: res.status || (res.progress_percent >= 100 ? "Completed" : "Active"),
          progress_percent: res.progress_percent,
          exercises_detail: updatedList
        };
      });

      // Update in allPlans list
      setAllPlans(prev =>
        prev.map(p =>
          p.plan_id === selectedPlan.plan_id
            ? {
                ...p,
                progress_percent: res.progress_percent,
                status: res.status || (res.progress_percent >= 100 ? "Completed" : "Active")
              }
            : p
        )
      );

      if (res.progress_percent >= 100) {
        setActionSuccess(`🎉 100% Completed! "${selectedPlan.title}" is fully completed and archived.`);
      } else {
        setActionSuccess(`Marked "${exerciseName}" as ${nextVal ? "Completed" : "Pending"}`);
      }
      setTimeout(() => setActionSuccess(""), 4000);
    } catch (err) {
      console.error("Failed to toggle task:", err);
    }
  };

  const handleReactivate = async (planId: string) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      await reactivateTrainingPlan(token, planId);

      // Refresh plan detail if currently open
      if (selectedPlan && selectedPlan.plan_id === planId) {
        const details = await getTrainingPlanDetail(token, planId);
        setSelectedPlan(details);
      }

      // Update list
      setAllPlans(prev =>
        prev.map(p =>
          p.plan_id === planId
            ? { ...p, status: "Active", progress_percent: 0 }
            : p
        )
      );

      setActionSuccess("Protocol reactivated! Moved back to Active Plans.");
      setTimeout(() => setActionSuccess(""), 3500);
    } catch (err) {
      console.error("Failed to reactivate plan:", err);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedPlan) return;
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      await updateTrainingPlan(token, selectedPlan.plan_id, { status: newStatus });
      setSelectedPlan(prev => (prev ? { ...prev, status: newStatus } : null));
      setAllPlans(prev =>
        prev.map(p => (p.plan_id === selectedPlan.plan_id ? { ...p, status: newStatus } : p))
      );
      setActionSuccess(`Plan status updated to ${newStatus}`);
      setTimeout(() => setActionSuccess(""), 3000);
    } catch (err) {
      console.error("Failed to update status:", err);
    }
  };

  // Compute Active vs Completed filtered plans
  const activePlans = allPlans.filter(
    p => (p.progress_percent || 0) < 100 && (p.status || "").toLowerCase() !== "completed"
  );
  const completedPlans = allPlans.filter(
    p => (p.progress_percent || 0) >= 100 || (p.status || "").toLowerCase() === "completed"
  );

  const displayedPlans = (
    activeTab === "active"
      ? activePlans
      : activeTab === "completed"
      ? completedPlans
      : allPlans
  ).filter(p => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.title.toLowerCase().includes(q) ||
      (p.target_joint && p.target_joint.toLowerCase().includes(q)) ||
      (p.focus && p.focus.toLowerCase().includes(q)) ||
      (p.description && p.description.toLowerCase().includes(q))
    );
  });

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16 animate-fadeIn">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <Link href="/dashboard" className="hover:text-indigo-400 transition-colors">
              Home
            </Link>
            <ChevronRight className="w-3 h-3 text-slate-600" />
            <Link href="/dashboard/recommendations" className="hover:text-indigo-400 transition-colors">
              Recommendations
            </Link>
            <ChevronRight className="w-3 h-3 text-slate-600" />
            <span className="text-indigo-400 font-medium">Training & Corrective Protocols</span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <Target className="w-7 h-7 text-indigo-400 shrink-0" />
            <span>Athletic Corrective Training Plans</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Activity-specific neuromuscular interventions, kinetic form cues, and joint-sparing prehab routines.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/recommendations"
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span>Clinical Recommendations</span>
          </Link>
          <Link
            href="/dashboard/upload"
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs text-white font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] flex items-center gap-1.5"
          >
            <PlayCircle className="w-3.5 h-3.5" />
            <span>Analyze Technique</span>
          </Link>
        </div>
      </div>

      {/* Global Success Banner */}
      {actionSuccess && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-slate-900 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2.5">
            <CheckCheck className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            Database Synchronized
          </span>
        </div>
      )}

      {/* Protocol Filtering Tabs & Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Tab Switcher */}
        <div className="flex items-center p-1 rounded-2xl bg-slate-900/90 border border-slate-800 w-fit">
          <button
            type="button"
            onClick={() => setActiveTab("active")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "active"
                ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            <span>Active Protocols</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-indigo-950 text-indigo-300 font-extrabold border border-indigo-500/30">
              {activePlans.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("completed")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "completed"
                ? "bg-emerald-600 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Completed Protocols</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-950 text-emerald-300 font-extrabold border border-emerald-500/30">
              {completedPlans.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("all")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "all"
                ? "bg-slate-800 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span>All ({allPlans.length})</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search exercises, joints..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
      </div>

      {/* Protocols Grid */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[30vh] text-slate-400">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm">Synchronizing clinical training plans...</span>
          </div>
        </div>
      ) : displayedPlans.length === 0 ? (
        <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
            {activeTab === "active" ? (
              <Award className="w-8 h-8 text-indigo-400" />
            ) : (
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            )}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              {activeTab === "active"
                ? "🎉 All Active Training Protocols Completed!"
                : activeTab === "completed"
                ? "No Completed Protocols Yet"
                : "No Protocols Matching Search"}
            </h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto leading-relaxed">
              {activeTab === "active"
                ? "Every assigned corrective protocol has reached 100% completion and been moved to the Completed archive. Run another video analysis to diagnose new biomechanical patterns or review past work."
                : activeTab === "completed"
                ? "As you check off all prescribed exercises in an active training plan and reach 100%, it will automatically archive here."
                : "Try a different search term or clear the filter."}
            </p>
          </div>
          {activeTab === "active" && completedPlans.length > 0 && (
            <button
              type="button"
              onClick={() => setActiveTab("completed")}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-indigo-300 transition-colors cursor-pointer"
            >
              View Completed Archive ({completedPlans.length}) &rarr;
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-6">
          {displayedPlans.map((plan) => {
            const isCompleted = (plan.progress_percent || 0) >= 100 || plan.status === "Completed";
            return (
              <div
                key={plan.id || plan.plan_id}
                className={`glass-panel p-6 sm:p-7 rounded-2xl border transition-all space-y-5 ${
                  isCompleted
                    ? "border-emerald-500/30 bg-emerald-950/5 hover:border-emerald-500/50"
                    : "border-slate-800 hover:border-slate-700/80"
                }`}
              >
                <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-white">{plan.title}</h3>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          isCompleted
                            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                            : plan.status === "Active"
                            ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                            : "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                        }`}
                      >
                        {isCompleted ? "Completed" : plan.status}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        <span>Duration:</span>
                        <strong className="text-slate-200">{plan.duration}</strong>
                      </span>
                      {plan.target_joint && (
                        <>
                          <span className="text-slate-600">•</span>
                          <span>
                            Target Joint: <strong className="text-indigo-300">{plan.target_joint}</strong>
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Progress Mini Bar */}
                  <div className="w-full sm:w-48 text-right">
                    <div className="flex justify-between items-center text-xs mb-1">
                      <span className="text-slate-400 font-medium">Protocol Progress</span>
                      <span
                        className={`font-bold ${
                          isCompleted ? "text-emerald-400" : "text-indigo-400"
                        }`}
                      >
                        {plan.progress_percent}%
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isCompleted
                            ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                            : "bg-gradient-to-r from-indigo-500 to-pink-500"
                        }`}
                        style={{ width: `${plan.progress_percent}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Prescribed Exercises List */}
                <div className="space-y-2 pt-2 border-t border-slate-800/80">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-400 uppercase tracking-wider">
                      Prescribed Clinical Exercises:
                    </span>
                    <span className="text-slate-500">{plan.tasks?.length || 0} Prescriptions</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {plan.tasks && plan.tasks.length > 0 ? (
                      plan.tasks.map((task, j) => (
                        <span
                          key={j}
                          className="px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-medium text-slate-200 flex items-center gap-2"
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              isCompleted ? "bg-emerald-400" : "bg-indigo-400"
                            }`}
                          ></span>
                          {task}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">No prescribed exercises logged yet.</span>
                    )}
                  </div>
                </div>

                {plan.description && (
                  <p className="text-xs text-slate-400 leading-relaxed">{plan.description}</p>
                )}

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row items-center gap-3 pt-1">
                  <button
                    type="button"
                    onClick={() => handleOpenPlanDetails(plan.plan_id)}
                    disabled={loadingDetail}
                    className="w-full sm:flex-1 py-2.5 px-4 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 hover:from-indigo-600 hover:to-pink-600 text-white text-xs font-bold rounded-xl border border-slate-800 hover:border-transparent transition-all shadow-sm hover:shadow-[0_0_20px_rgba(79,70,229,0.3)] flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <PlayCircle className="w-4 h-4 text-indigo-400" />
                    <span>View Prescribed Exercises & Form Cues</span>
                  </button>

                  {isCompleted && (
                    <button
                      type="button"
                      onClick={() => handleReactivate(plan.plan_id)}
                      className="w-full sm:w-auto py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold rounded-xl border border-slate-800 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                    >
                      <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
                      <span>Restart Protocol</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Full Plan Details Modal */}
      {selectedPlan && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto animate-fadeIn">
          <div className="glass-panel w-full max-w-4xl max-h-[92vh] rounded-3xl border border-slate-700 p-6 sm:p-8 overflow-y-auto space-y-6 relative shadow-[0_0_50px_rgba(0,0,0,0.8)]">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-800">
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-2xl font-extrabold text-white">{selectedPlan.title}</h3>
                  <span
                    className={`text-xs font-bold px-3 py-0.5 rounded-full uppercase tracking-wider ${
                      selectedPlan.progress_percent >= 100 || selectedPlan.status === "Completed"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                        : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                    }`}
                  >
                    {selectedPlan.progress_percent >= 100 ? "Completed" : selectedPlan.status}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                  <span>
                    Duration: <strong className="text-slate-200">{selectedPlan.duration}</strong>
                  </span>
                  <span className="text-slate-600">•</span>
                  <span>
                    Target Axis: <strong className="text-indigo-400">{selectedPlan.target_joint}</strong>
                  </span>
                  {selectedPlan.focus && (
                    <>
                      <span className="text-slate-600">•</span>
                      <span>
                        Focus: <strong className="text-slate-300">{selectedPlan.focus}</strong>
                      </span>
                    </>
                  )}
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedPlan(null)}
                className="w-9 h-9 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors cursor-pointer shrink-0"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Completion Celebration Alert */}
            {selectedPlan.progress_percent >= 100 ? (
              <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/50 via-slate-900 to-slate-900 border border-emerald-500/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                    <span className="text-sm font-bold text-white">
                      100% Protocol Achieved & Archived
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    All prescribed neuromuscular exercises have been verified. This plan is now archived and automatically removed from your active training queue.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => handleReactivate(selectedPlan.plan_id)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] shrink-0 flex items-center gap-1.5 cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Restart Protocol</span>
                </button>
              </div>
            ) : (
              /* Protocol Adherence Rate Banner */
              <div className="p-4 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-slate-900 to-indigo-950/40 border border-indigo-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <div className="text-xs font-semibold uppercase text-indigo-400 tracking-wider">
                    Protocol Adherence Rate
                  </div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {selectedPlan.progress_percent}% Completed
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Check off exercises below as you execute each session to log completion.
                  </div>
                </div>
                <div className="w-full sm:w-56">
                  <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-300"
                      style={{ width: `${selectedPlan.progress_percent}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Description & Clinical Notes */}
            <div className="space-y-3">
              <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                <strong className="text-white block mb-1 text-sm font-semibold">
                  Biomechanical Objective:
                </strong>
                {selectedPlan.description}
              </div>

              {selectedPlan.clinical_notes && (
                <div className="bg-indigo-950/20 p-4 rounded-xl border border-indigo-500/20 text-xs text-indigo-200/90 leading-relaxed">
                  <strong className="text-indigo-300 block mb-1 font-semibold flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    Sports Scientist Clinical Notes:
                  </strong>
                  {selectedPlan.clinical_notes}
                </div>
              )}
            </div>

            {/* Prescribed Exercise Protocols */}
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h4 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
                  <Zap className="w-4 h-4 text-pink-400" />
                  Prescribed Exercise Protocols & Biomechanical Rationale:
                </h4>
                <span className="text-xs text-slate-400">
                  {selectedPlan.exercises_detail?.filter(e => e.completed).length || 0} of{" "}
                  {selectedPlan.exercises_detail?.length || 0} Completed
                </span>
              </div>

              <div className="grid gap-4">
                {selectedPlan.exercises_detail && selectedPlan.exercises_detail.length > 0 ? (
                  selectedPlan.exercises_detail.map((ex, idx) => (
                    <div
                      key={idx}
                      className={`p-5 rounded-2xl border transition-all ${
                        ex.completed
                          ? "bg-emerald-950/15 border-emerald-500/30"
                          : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2.5">
                            <span className="text-base font-bold text-white">{ex.name}</span>
                            {ex.alias && <span className="text-xs text-slate-400">({ex.alias})</span>}
                          </div>
                          {ex.target_muscles && (
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {ex.target_muscles.map((m, mi) => (
                                <span
                                  key={mi}
                                  className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-indigo-300 font-medium"
                                >
                                  {m}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Interactive Task Completion Toggle */}
                        <button
                          type="button"
                          onClick={() => handleToggleTask(ex.name, Boolean(ex.completed))}
                          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
                            ex.completed
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30"
                              : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]"
                          }`}
                        >
                          {ex.completed ? (
                            <>
                              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                              <span>Completed</span>
                            </>
                          ) : (
                            <>
                              <span className="w-3.5 h-3.5 rounded border border-white/60"></span>
                              <span>Mark Complete</span>
                            </>
                          )}
                        </button>
                      </div>

                      {/* Protocol Parameters */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
                        <div>
                          <span className="text-slate-500 block text-[11px]">Sets & Reps:</span>
                          <strong className="text-slate-200">
                            {ex.sets} Sets × {ex.reps}
                          </strong>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[11px]">Rest Interval:</span>
                          <strong className="text-slate-200">{ex.rest || "45 sec"}</strong>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[11px]">Movement Tempo:</span>
                          <strong className="text-slate-200">{ex.tempo || "Controlled"}</strong>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[11px]">Prescribed Frequency:</span>
                          <strong className="text-indigo-400">{ex.frequency || "3x / week"}</strong>
                        </div>
                      </div>

                      {/* Biomechanical Rationale */}
                      {ex.biomechanical_rationale && (
                        <div className="text-xs text-slate-300 leading-relaxed mb-2">
                          <strong className="text-indigo-400">Biomechanical Rationale: </strong>
                          {ex.biomechanical_rationale}
                        </div>
                      )}

                      {/* Coaching Cues */}
                      {ex.form_cues && ex.form_cues.length > 0 && (
                        <div className="space-y-1 text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                          <strong className="text-slate-300 text-[11px] uppercase tracking-wider block">
                            Key Technique Cues:
                          </strong>
                          <ul className="list-disc list-inside space-y-0.5">
                            {ex.form_cues.map((cue, ci) => (
                              <li key={ci} className="text-slate-300">
                                {cue}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="p-4 rounded-xl bg-slate-900 text-xs text-slate-400">
                    No individual exercises detailed.
                  </div>
                )}
              </div>
            </div>

            {/* Weekly Progression / Periodization Breakdown */}
            {selectedPlan.weekly_schedule && selectedPlan.weekly_schedule.length > 0 && (
              <div className="space-y-3 pt-2">
                <h4 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  Periodization & Progression Schedule:
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {selectedPlan.weekly_schedule.map((sch, si) => (
                    <div
                      key={si}
                      className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5"
                    >
                      <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                        {sch.week || sch.phase || `Phase ${si + 1}`}
                      </div>
                      <div className="text-xs font-semibold text-white leading-snug">
                        {sch.objective}
                      </div>
                      <div className="text-[11px] text-slate-400 leading-relaxed pt-1 border-t border-slate-800/80">
                        {sch.intensity}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Modal Bottom Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <Link
                  href="/dashboard/upload"
                  className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-500/20 text-center w-full sm:w-auto"
                >
                  Verify Form in Video Engine &rarr;
                </Link>
                <Link
                  href="/dashboard/recommendations"
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors text-center w-full sm:w-auto"
                >
                  Back to Recommendations &rarr;
                </Link>
              </div>

              <button
                type="button"
                onClick={() => setSelectedPlan(null)}
                className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl border border-slate-700 transition-colors w-full sm:w-auto cursor-pointer"
              >
                Close Plan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TrainingPlansPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[50vh] text-slate-400">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm">Loading training plans...</span>
          </div>
        </div>
      }
    >
      <TrainingPlansContent />
    </Suspense>
  );
}
