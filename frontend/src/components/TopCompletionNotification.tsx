"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAnalysis, ActiveNotification } from "@/context/AnalysisContext";
import { CheckCircle2, ArrowRight, X, Sparkles, GitCompare } from "lucide-react";

interface TopNotificationCardProps {
  notification: ActiveNotification;
  onDismiss: () => void;
}

const TOTAL_VANISH_SECONDS = 7;

function TopNotificationCard({ notification, onDismiss }: TopNotificationCardProps) {
  const router = useRouter();

  // Compute remaining seconds based on persistent wall-clock timestamp
  const calculateRemainingSeconds = () => {
    const elapsedSeconds = (Date.now() - notification.timestamp) / 1000;
    const remaining = Math.max(0, Math.ceil(TOTAL_VANISH_SECONDS - elapsedSeconds));
    return remaining;
  };

  const [timeLeft, setTimeLeft] = useState(calculateRemainingSeconds);

  useEffect(() => {
    const tick = () => {
      const remaining = calculateRemainingSeconds();
      setTimeLeft(remaining);
      if (remaining <= 0) {
        onDismiss();
      }
    };

    tick();
    const interval = setInterval(tick, 250);

    return () => {
      clearInterval(interval);
    };
  }, [notification.timestamp, onDismiss]);

  const handleNavigate = (e: React.MouseEvent) => {
    e.preventDefault();
    router.push(notification.link);
    onDismiss();
  };

  const isDual = notification.type === "dual";
  const progressRatio = Math.max(0, Math.min(1, timeLeft / TOTAL_VANISH_SECONDS));

  return (
    <div className="relative overflow-hidden rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-emerald-500/50 shadow-[0_15px_40px_-10px_rgba(16,185,129,0.35)] p-4 sm:p-5 text-white animate-in fade-in slide-in-from-top-6 duration-300">
      {/* Ambient Top Glow Bar with 7-second countdown */}
      <div
        className="absolute top-0 left-0 h-1 bg-gradient-to-r from-emerald-400 via-sky-400 to-indigo-500 transition-all ease-linear"
        style={{
          width: `${progressRatio * 100}%`,
          transitionDuration: "250ms"
        }}
      />

      <div className="flex items-start gap-3.5">
        {/* Icon Badge */}
        <div className="p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 shrink-0 mt-0.5">
          {isDual ? <GitCompare className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
        </div>

        {/* Text Content */}
        <div className="flex-1 min-w-0 pr-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              <CheckCircle2 className="w-3 h-3 mr-1" /> Ready
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Auto-closing in {timeLeft}s
            </span>
            <h4 className="font-bold text-base text-white tracking-wide truncate">
              {notification.title}
            </h4>
          </div>

          <p className="text-slate-300 text-xs sm:text-sm mt-1 leading-relaxed">
            {notification.message}
          </p>

          {/* Hyperlink Action Button */}
          <div className="mt-3">
            <button
              onClick={handleNavigate}
              className="inline-flex items-center gap-2 text-xs sm:text-sm font-semibold text-emerald-400 hover:text-emerald-300 bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-500/40 rounded-xl px-3.5 py-1.5 transition-all duration-200 group shadow-sm cursor-pointer"
            >
              <span>{notification.linkText}</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>

        {/* Cross Mark Discard Button */}
        <button
          type="button"
          onClick={onDismiss}
          title="Discard notification"
          aria-label="Discard notification"
          className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center transition-all cursor-pointer border border-white/10 shrink-0 mt-0.5"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default function TopCompletionNotification() {
  const { activeNotifications, dismissNotification } = useAnalysis();

  if (!activeNotifications || activeNotifications.length === 0) return null;

  return (
    <div className="fixed top-5 left-1/2 -translate-x-1/2 z-[9999] w-[94%] max-w-xl flex flex-col gap-3 pointer-events-auto">
      {activeNotifications.map((notif) => (
        <TopNotificationCard
          key={notif.id}
          notification={notif}
          onDismiss={() => dismissNotification(notif.id)}
        />
      ))}
    </div>
  );
}
