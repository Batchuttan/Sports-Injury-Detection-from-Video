"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAnalysis } from "@/context/AnalysisContext";
import { Film, GitCompare, ExternalLink, Loader2, X } from "lucide-react";

interface ProgressBadgeItemProps {
  type: "single" | "dual";
  progress: number;
  stage: string;
  title: string;
  fileSubtitle: string;
  targetLink: string;
}

function ProgressBadgeItem({
  type,
  progress,
  stage,
  title,
  fileSubtitle,
  targetLink
}: ProgressBadgeItemProps) {
  const pathname = usePathname();
  const [isDismissed, setIsDismissed] = useState(false);
  const [timeLeft, setTimeLeft] = useState(7);

  const roundedProgress = Math.round(progress);
  const isCurrentPage = pathname === targetLink;
  const isDual = type === "dual";

  // When job starts or route changes, count down 7 seconds before vanishing
  useEffect(() => {
    setIsDismissed(false);
    setTimeLeft(7);

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setIsDismissed(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    const vanishTimer = setTimeout(() => {
      setIsDismissed(true);
    }, 7000);

    return () => {
      clearInterval(interval);
      clearTimeout(vanishTimer);
    };
  }, [pathname]);

  if (isDismissed) return null;

  return (
    <div className="relative overflow-hidden rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-indigo-500/40 shadow-[0_15px_35px_-5px_rgba(79,70,229,0.35)] p-4 text-white animate-in fade-in slide-in-from-right-6 duration-300">
      {/* Subtle top indicator bar with 7-second countdown */}
      <div
        className="absolute top-0 left-0 h-1 bg-gradient-to-r from-indigo-500 via-sky-400 to-emerald-400 transition-all ease-linear"
        style={{
          width: `${(timeLeft / 7) * 100}%`,
          transitionDuration: "1000ms"
        }}
      />

      {/* Header with Title and Cross Mark Discard Button */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500" />
          </span>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-indigo-300">
            Background Processing ({timeLeft}s)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs font-bold text-sky-400 bg-sky-950/60 px-2 py-0.5 rounded-md border border-sky-500/30">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>{roundedProgress}%</span>
          </div>

          {/* Cross Mark Discard Button */}
          <button
            type="button"
            onClick={() => setIsDismissed(true)}
            title="Discard notification"
            aria-label="Discard notification"
            className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center transition-all cursor-pointer border border-white/10 shrink-0"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Title & File Info */}
      <div className="mb-2.5">
        <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
          {isDual ? <GitCompare className="w-4 h-4 text-indigo-400" /> : <Film className="w-4 h-4 text-indigo-400" />}
          <span>{title}</span>
        </h4>
        <p className="text-xs text-slate-300 truncate mt-0.5" title={fileSubtitle}>
          {fileSubtitle}
        </p>
      </div>

      {/* Animated Percentage Bar (Like Downloading a Game) */}
      <div className="space-y-1.5 mb-3">
        <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700/60">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-sky-400 to-emerald-400 transition-all duration-300 ease-out rounded-full relative overflow-hidden"
            style={{ width: `${Math.min(100, Math.max(3, roundedProgress))}%` }}
          >
            {/* Shimmer light effect */}
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
          </div>
        </div>
        <p className="text-[11px] text-slate-400 truncate italic">
          {stage || "Running biomechanical computer vision pipeline..."}
        </p>
      </div>

      {/* Tab Switch Navigation Link */}
      {!isCurrentPage && (
        <div className="pt-1 border-t border-slate-800">
          <Link
            href={targetLink}
            className="inline-flex items-center justify-between w-full text-xs font-medium text-indigo-300 hover:text-white bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-500/30 rounded-xl px-3 py-1.5 transition-all duration-200"
          >
            <span>Switch to Active Tab</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}
    </div>
  );
}

export default function FloatingProgressBadge() {
  const {
    isAnalyzingSingle,
    singleProgress,
    singleStage,
    singleFileName,
    isComparingDual,
    dualProgress,
    dualStage,
    dualFileAName,
    dualFileBName,
    showProgressBadge
  } = useAnalysis();

  // If user disabled floating badge in settings or neither is active, do not render
  if (!showProgressBadge || (!isAnalyzingSingle && !isComparingDual)) return null;

  return (
    <div className="fixed top-20 right-5 z-[9990] w-84 max-w-[calc(100vw-2.5rem)] flex flex-col gap-3 pointer-events-auto">
      {/* If single video analysis is running */}
      {isAnalyzingSingle && (
        <ProgressBadgeItem
          key="single-progress"
          type="single"
          progress={singleProgress}
          stage={singleStage}
          title="Video Analysis"
          fileSubtitle={singleFileName || "Athletic Video"}
          targetLink="/dashboard/upload"
        />
      )}

      {/* If dual video comparison is running */}
      {isComparingDual && (
        <ProgressBadgeItem
          key="dual-progress"
          type="dual"
          progress={dualProgress}
          stage={dualStage}
          title="Dual Video Comparison"
          fileSubtitle={`${dualFileAName || "Video 1"} vs ${dualFileBName || "Video 2"}`}
          targetLink="/dashboard/compare"
        />
      )}
    </div>
  );
}
