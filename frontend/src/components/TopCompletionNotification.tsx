"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAnalysis } from "@/context/AnalysisContext";
import { CheckCircle2, ArrowRight, X, Sparkles, Film, GitCompare } from "lucide-react";

export default function TopCompletionNotification() {
  const { activeNotification, dismissNotification } = useAnalysis();
  const router = useRouter();

  if (!activeNotification) return null;

  const handleNavigate = (e: React.MouseEvent) => {
    e.preventDefault();
    router.push(activeNotification.link);
    dismissNotification();
  };

  const isDual = activeNotification.type === "dual";

  return (
    <div className="fixed top-5 left-1/2 -translate-x-1/2 z-[9999] w-[94%] max-w-xl animate-in fade-in slide-in-from-top-6 duration-300 pointer-events-auto">
      <div className="relative overflow-hidden rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-emerald-500/50 shadow-[0_15px_40px_-10px_rgba(16,185,129,0.35)] p-4 sm:p-5 text-white">
        {/* Ambient Top Glow Bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 via-sky-400 to-indigo-500" />

        <div className="flex items-start gap-3.5">
          {/* Icon Badge */}
          <div className="p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 shrink-0 mt-0.5">
            {isDual ? <GitCompare className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
          </div>

          {/* Text Content */}
          <div className="flex-1 min-w-0 pr-6">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <CheckCircle2 className="w-3 h-3 mr-1" /> Ready
              </span>
              <h4 className="font-bold text-base text-white tracking-wide truncate">
                {activeNotification.title}
              </h4>
            </div>

            <p className="text-slate-300 text-xs sm:text-sm mt-1 leading-relaxed">
              {activeNotification.message}
            </p>

            {/* Hyperlink Action Button */}
            <div className="mt-3">
              <button
                onClick={handleNavigate}
                className="inline-flex items-center gap-2 text-xs sm:text-sm font-semibold text-emerald-400 hover:text-emerald-300 bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-500/40 rounded-xl px-3.5 py-1.5 transition-all duration-200 group shadow-sm"
              >
                <span>{activeNotification.linkText}</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </button>
            </div>
          </div>

          {/* Dismiss 'X' Button */}
          <button
            onClick={dismissNotification}
            aria-label="Dismiss notification"
            className="absolute top-3.5 right-3.5 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
