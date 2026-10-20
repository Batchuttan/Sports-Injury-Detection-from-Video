"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getUserFromToken } from "@/lib/auth";
import { requestPasswordChange } from "@/lib/api";

export default function SettingsPage() {
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);

  // Email Alerts & Preferences state
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [dailyWellness, setDailyWellness] = useState(true);
  const [soundEffects, setSoundEffects] = useState(false);

  // Password Change state
  const [requestingPasswordChange, setRequestingPasswordChange] = useState(false);
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState("");
  const [passwordChangeError, setPasswordChangeError] = useState("");

  useEffect(() => {
    const fetched = getUserFromToken();
    if (fetched) {
      setUser(fetched);
    }
  }, []);

  const handleRequestPasswordChange = async () => {
    setPasswordChangeError("");
    setPasswordChangeSuccess("");
    setRequestingPasswordChange(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authorization token found. Please log in again.");

      const res = await requestPasswordChange(token);
      setPasswordChangeSuccess(res.message || "A secure confirmation link was sent to your email!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to initiate password change.";
      setPasswordChangeError(msg);
    } finally {
      setRequestingPasswordChange(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div>
        <h2 className="text-2xl font-bold text-white">Account & System Settings</h2>
        <p className="text-slate-400 text-sm mt-1">
          Manage your biometric profile security, email verification protocols, and alert preferences.
        </p>
      </div>

      {/* Account Info Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-pink-500 flex items-center justify-center text-white font-extrabold text-xl shadow-[0_0_20px_rgba(79,70,229,0.3)]">
            {user?.email ? user.email.substring(0, 2).toUpperCase() : "AI"}
          </div>
          <div>
            <div className="text-white font-semibold text-lg">{user?.email || "demo@sportsai.com"}</div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-400 font-medium">
                {user?.role || "Athlete"}
              </span>
              <span className="text-xs text-slate-500">• 2-Factor Email Verified</span>
            </div>
          </div>
        </div>
        <div className="text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-medium flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Active Security Protocol
        </div>
      </div>

      {/* Security & Password Change Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <h3 className="text-lg font-bold text-white">Security & Password Management</h3>
          </div>
          <p className="text-slate-400 text-sm">
            To prevent unauthorized account takeovers, password modifications require verification via an authenticated email link.
          </p>
        </div>

        {passwordChangeError && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
            {passwordChangeError}
          </div>
        )}

        {passwordChangeSuccess && (
          <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm space-y-3">
            <div className="flex items-center gap-2 font-semibold text-emerald-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Confirmation Email Dispatched!
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              We have dispatched a verification email to <strong>{user?.email || "your registered address"}</strong> containing a secure link valid for 30 minutes. Click the link in your email to confirm and submit your new password.
            </p>
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
          <div>
            <div className="text-white font-medium text-sm">Change Account Password</div>
            <div className="text-xs text-slate-400 mt-0.5">
              Send a cryptographically signed confirmation link to {user?.email || "your email"}
            </div>
          </div>
          <button
            onClick={handleRequestPasswordChange}
            disabled={requestingPasswordChange}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] hover:shadow-[0_0_20px_rgba(79,70,229,0.5)] flex items-center gap-2 shrink-0"
          >
            {requestingPasswordChange ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Sending Link...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Send Password Change Email
              </>
            )}
          </button>
        </div>
      </div>

      {/* Notifications Preferences */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">Notification & Alert Preferences</h3>
          <p className="text-slate-400 text-sm">Configure how biomechanical threshold violations and recovery reminders are delivered.</p>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <div>
              <div className="text-white font-medium text-sm">Biomechanical Anomaly Alerts (Email)</div>
              <div className="text-xs text-slate-400 mt-0.5">Receive instant alerts when knee valgus or trunk lean exceed critical thresholds</div>
            </div>
            <button
              onClick={() => setEmailAlerts(!emailAlerts)}
              className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${emailAlerts ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-transform ${emailAlerts ? "right-1" : "left-1"}`} />
            </button>
          </div>

          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <div>
              <div className="text-white font-medium text-sm">Daily Wellness & Fatigue Prompt</div>
              <div className="text-xs text-slate-400 mt-0.5">Daily reminder to enter perceived exertion (RPE) and sleep quality metrics</div>
            </div>
            <button
              onClick={() => setDailyWellness(!dailyWellness)}
              className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${dailyWellness ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-transform ${dailyWellness ? "right-1" : "left-1"}`} />
            </button>
          </div>

          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <div>
              <div className="text-white font-medium text-sm">Video Processing Audio Cues</div>
              <div className="text-xs text-slate-400 mt-0.5">Play subtle audio notification upon completing pose estimation rendering</div>
            </div>
            <button
              onClick={() => setSoundEffects(!soundEffects)}
              className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${soundEffects ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-transform ${soundEffects ? "right-1" : "left-1"}`} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
