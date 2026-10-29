"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { getUserFromToken } from "@/lib/auth";
import { requestPasswordChange, getUserSettings, updateUserSettings, uploadUserAvatar } from "@/lib/api";

export default function SettingsPage() {
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);
  const [profilePicture, setProfilePicture] = useState<string>("");
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  // Email Alerts & Preferences state with real backend sync
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [dailyWellness, setDailyWellness] = useState(true);
  const [soundEffects, setSoundEffects] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState("");

  // Password Change state
  const [requestingPasswordChange, setRequestingPasswordChange] = useState(false);
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState("");
  const [passwordChangeError, setPasswordChangeError] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Play subtle chime using Web Audio API
  const playSubtleChime = () => {
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.12); // A5

      gain.gain.setValueAtTime(0.18, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) {
      console.warn("Audio cue playback error:", e);
    }
  };

  useEffect(() => {
    const fetched = getUserFromToken();
    if (fetched) {
      setUser(fetched);
    }

    const loadSettings = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;
        const data = await getUserSettings(token);
        if (data) {
          setEmailAlerts(Boolean(data.email_alerts));
          setDailyWellness(Boolean(data.daily_wellness));
          setSoundEffects(Boolean(data.sound_effects));
          if (data.profile_picture) {
            setProfilePicture(data.profile_picture);
            localStorage.setItem("user_avatar", data.profile_picture);
          }
        }
      } catch (err) {
        console.warn("Could not retrieve backend settings, using cached values:", err);
      }
    };

    loadSettings();
  }, []);

  const handleToggle = async (key: "email_alerts" | "daily_wellness" | "sound_effects", nextVal: boolean) => {
    if (key === "email_alerts") setEmailAlerts(nextVal);
    if (key === "daily_wellness") setDailyWellness(nextVal);
    if (key === "sound_effects") {
      setSoundEffects(nextVal);
      if (nextVal) {
        playSubtleChime();
      }
    }

    setSavingSettings(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      await updateUserSettings(token, { [key]: nextVal });
      setSaveSuccessMsg("Preferences saved to backend successfully!");
      setTimeout(() => setSaveSuccessMsg(""), 3000);
    } catch (err) {
      console.error("Failed to save setting:", err);
    } finally {
      setSavingSettings(false);
    }
  };

  const handleAvatarFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingAvatar(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token found");

      const res = await uploadUserAvatar(token, file);
      if (res && res.profile_picture) {
        setProfilePicture(res.profile_picture);
        localStorage.setItem("user_avatar", res.profile_picture);
        window.dispatchEvent(new Event("avatar_updated"));
        setSaveSuccessMsg("Profile photo updated successfully!");
        setTimeout(() => setSaveSuccessMsg(""), 3500);
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to upload photo");
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleRemoveAvatar = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      await updateUserSettings(token, { profile_picture: "" });
      setProfilePicture("");
      localStorage.removeItem("user_avatar");
      window.dispatchEvent(new Event("avatar_updated"));
      setSaveSuccessMsg("Profile photo reset to default initials avatar.");
      setTimeout(() => setSaveSuccessMsg(""), 3500);
    } catch (err) {
      console.error(err);
    }
  };

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

      {saveSuccessMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-sm flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>{saveSuccessMsg}</span>
          </div>
          <span className="text-xs text-emerald-400 font-mono">Backend Synced</span>
        </div>
      )}

      {/* Account Info Card with Profile Photo Edit & View */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-5">
          {/* Avatar Container */}
          <div className="relative group">
            {profilePicture ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={profilePicture}
                alt="Profile Avatar"
                className="w-16 h-16 rounded-2xl object-cover border-2 border-indigo-500 shadow-[0_0_20px_rgba(79,70,229,0.35)]"
              />
            ) : (
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-pink-500 flex items-center justify-center text-white font-extrabold text-2xl shadow-[0_0_20px_rgba(79,70,229,0.3)]">
                {user?.email ? user.email.substring(0, 2).toUpperCase() : "AI"}
              </div>
            )}

            {/* Quick Upload Hover Overlay */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingAvatar}
              title="Change Profile Picture"
              className="absolute inset-0 bg-black/60 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white text-xs font-semibold"
            >
              <svg className="w-5 h-5 text-indigo-300 mb-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Edit
            </button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleAvatarFileChange}
          />

          <div>
            <div className="text-white font-semibold text-lg flex items-center gap-2">
              <span>{user?.email || "demo@sportsai.com"}</span>
              {uploadingAvatar && (
                <span className="text-xs text-indigo-400 animate-pulse font-normal">(Uploading...)</span>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-400 font-medium">
                {user?.role || "Athlete"}
              </span>
              <span className="text-xs text-slate-500">• 2-Factor Email Verified</span>
            </div>
            <div className="flex items-center gap-3 mt-2 text-xs">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="text-indigo-400 hover:text-indigo-300 font-medium underline underline-offset-2 transition-colors cursor-pointer"
              >
                {profilePicture ? "Change Profile Photo" : "Upload Profile Photo"}
              </button>
              {profilePicture && (
                <>
                  <span className="text-slate-600">|</span>
                  <button
                    type="button"
                    onClick={handleRemoveAvatar}
                    className="text-rose-400 hover:text-rose-300 font-medium transition-colors cursor-pointer"
                  >
                    Reset to Default Initials
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-end md:items-center gap-3">
          <div className="text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-medium flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Active Security Protocol
          </div>
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
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] hover:shadow-[0_0_20px_rgba(79,70,229,0.5)] flex items-center gap-2 shrink-0 cursor-pointer"
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

      {/* Notifications & Alert Preferences */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-1">Notification & Alert Preferences</h3>
            <p className="text-slate-400 text-sm">Configure how biomechanical threshold violations and recovery reminders are delivered.</p>
          </div>
          {savingSettings && (
            <span className="text-xs text-indigo-400 flex items-center gap-1.5 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
              Saving...
            </span>
          )}
        </div>

        <div className="space-y-4">
          {/* Biomechanical Anomaly Alerts (Email) */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/40 border border-slate-800/60 hover:border-slate-700/60 transition-colors">
            <div className="pr-4">
              <div className="text-white font-medium text-sm flex items-center gap-2">
                <span>Biomechanical Anomaly Alerts (Email)</span>
                {emailAlerts ? (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">Active</span>
                ) : (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-500">Muted</span>
                )}
              </div>
              <div className="text-xs text-slate-400 mt-1">Receive instant alerts when knee valgus or trunk lean exceed critical thresholds</div>
            </div>
            <button
              type="button"
              onClick={() => handleToggle("email_alerts", !emailAlerts)}
              className={`w-14 h-7 rounded-full transition-colors relative cursor-pointer shrink-0 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 ${emailAlerts ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-all ${emailAlerts ? "right-1" : "left-1"}`} />
            </button>
          </div>

          {/* Daily Wellness & Fatigue Prompt */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/40 border border-slate-800/60 hover:border-slate-700/60 transition-colors">
            <div className="pr-4">
              <div className="text-white font-medium text-sm flex items-center gap-2">
                <span>Daily Wellness & Fatigue Prompt</span>
                {dailyWellness ? (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">Daily 8:00 AM</span>
                ) : (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-500">Disabled</span>
                )}
              </div>
              <div className="text-xs text-slate-400 mt-1">Daily reminder to enter perceived exertion (RPE) and sleep quality metrics</div>
            </div>
            <button
              type="button"
              onClick={() => handleToggle("daily_wellness", !dailyWellness)}
              className={`w-14 h-7 rounded-full transition-colors relative cursor-pointer shrink-0 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 ${dailyWellness ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-all ${dailyWellness ? "right-1" : "left-1"}`} />
            </button>
          </div>

          {/* Video Processing Audio Cues */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/40 border border-slate-800/60 hover:border-slate-700/60 transition-colors">
            <div className="pr-4">
              <div className="text-white font-medium text-sm flex items-center gap-2">
                <span>Video Processing Audio Cues</span>
                {soundEffects ? (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">Sound On</span>
                ) : (
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-500">Silent</span>
                )}
              </div>
              <div className="text-xs text-slate-400 mt-1">Play subtle audio notification upon completing pose estimation rendering</div>
              <button
                type="button"
                onClick={playSubtleChime}
                className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium cursor-pointer"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                </svg>
                Preview Chime Tone
              </button>
            </div>
            <button
              type="button"
              onClick={() => handleToggle("sound_effects", !soundEffects)}
              className={`w-14 h-7 rounded-full transition-colors relative cursor-pointer shrink-0 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 ${soundEffects ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-all ${soundEffects ? "right-1" : "left-1"}`} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
