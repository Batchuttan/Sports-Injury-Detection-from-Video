"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { getAthleteProfile, createAthleteProfile, updateAthleteProfile, uploadUserAvatar } from "@/lib/api";
import { getUserFromToken } from "@/lib/auth";

interface ProfileData {
  id?: number;
  user_id: number;
  sport_type: string;
  position: string;
  age: number;
  height: number;
  weight: number;
  injury_history: string;
  training_load: string;
  phone?: string;
  dominant_side?: string;
  emergency_contact?: string;
  personal_bio?: string;
  profile_picture?: string;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [userEmail, setUserEmail] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [uploadingPic, setUploadingPic] = useState(false);

  const [formData, setFormData] = useState({
    sport_type: "",
    position: "",
    age: "",
    height: "",
    weight: "",
    injury_history: "",
    training_load: "",
    phone: "",
    dominant_side: "",
    emergency_contact: "",
    personal_bio: "",
    profile_picture: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadProfile = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const user = getUserFromToken();
      if (user?.email) setUserEmail(user.email);

      const data = await getAthleteProfile(token);
      if (data) {
        setProfile(data);
        setFormData({
          sport_type: data.sport_type || "Football",
          position: data.position || "Left Back",
          age: data.age?.toString() || "20",
          height: data.height?.toString() || "170",
          weight: data.weight?.toString() || "50",
          injury_history: data.injury_history || "Small bone cracks on right leg and recent crack on right leg small finger",
          training_load: data.training_load || "Football camp",
          phone: data.phone || "+1 (555) 234-8901",
          dominant_side: data.dominant_side || "Left Foot",
          emergency_contact: data.emergency_contact || "Dr. Marcus Vance (Physio) - +1 (555) 019-2834",
          personal_bio: data.personal_bio || "Left-back athlete dedicated to offensive wing overloads and defensive recovery transitions.",
          profile_picture: data.profile_picture || "",
        });

        if (data.profile_picture) {
          localStorage.setItem("user_avatar", data.profile_picture);
          window.dispatchEvent(new Event("avatar_updated"));
        }
      } else {
        setIsEditing(true);
      }
    } catch (err) {
      console.error("Error loading athlete profile:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleProfilePicChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingPic(true);
    setError("");
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authorization token found");

      const res = await uploadUserAvatar(token, file);
      if (res && res.profile_picture) {
        setFormData(prev => ({ ...prev, profile_picture: res.profile_picture }));
        setProfile(prev => prev ? { ...prev, profile_picture: res.profile_picture } : null);
        localStorage.setItem("user_avatar", res.profile_picture);
        window.dispatchEvent(new Event("avatar_updated"));
        setSuccess("Profile picture uploaded and updated successfully!");
        setTimeout(() => setSuccess(""), 3500);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to upload photo");
    } finally {
      setUploadingPic(false);
    }
  };

  const handleRemoveProfilePic = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const payload = { ...formData, profile_picture: "" };
      await updateAthleteProfile(token, payload);
      setFormData(prev => ({ ...prev, profile_picture: "" }));
      setProfile(prev => prev ? { ...prev, profile_picture: "" } : null);
      localStorage.removeItem("user_avatar");
      window.dispatchEvent(new Event("avatar_updated"));
      setSuccess("Profile picture reverted to default avatar.");
      setTimeout(() => setSuccess(""), 3500);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token found");

      const payload = {
        ...formData,
        age: parseInt(formData.age, 10) || 20,
        height: parseFloat(formData.height) || 170.0,
        weight: parseFloat(formData.weight) || 50.0,
      };

      if (profile) {
        const updated = await updateAthleteProfile(token, payload);
        setProfile(updated);
        setSuccess("Athlete profile successfully updated!");
      } else {
        const created = await createAthleteProfile(token, payload);
        setProfile(created);
        setSuccess("Athlete profile successfully created!");
      }
      setIsEditing(false);
      window.dispatchEvent(new Event("avatar_updated"));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const heightM = (parseFloat(formData.height) || 170) / 100;
  const weightKg = parseFloat(formData.weight) || 50;
  const bmi = (weightKg / (heightM * heightM)).toFixed(1);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-slate-400">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading athlete profile records...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Page Title & Actions */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Athlete Profile Management</h2>
          <p className="text-slate-400 text-sm mt-1">
            Manage your physical assessment records, injury history, and training profiles.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all font-semibold text-sm shadow-[0_0_15px_rgba(79,70,229,0.3)] flex items-center gap-2 cursor-pointer"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Edit Profile
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors font-medium text-sm border border-slate-700 cursor-pointer"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-sm font-medium flex items-center gap-2">
          <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      {success && (
        <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-sm font-medium flex items-center gap-2">
          <svg className="w-5 h-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {success}
        </div>
      )}

      {/* Hero Profile Card */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div className="flex items-center gap-5">
            {/* Avatar View & Change Trigger */}
            <div className="relative group shrink-0">
              {profile?.profile_picture ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={profile.profile_picture}
                  alt="Athlete Avatar"
                  className="w-20 h-20 rounded-2xl object-cover border-2 border-indigo-500 shadow-[0_0_25px_rgba(79,70,229,0.4)]"
                />
              ) : (
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 to-pink-500 flex items-center justify-center text-white font-extrabold text-3xl shadow-[0_0_25px_rgba(79,70,229,0.3)]">
                  {userEmail ? userEmail.substring(0, 2).toUpperCase() : "AI"}
                </div>
              )}

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingPic}
                className="absolute inset-0 bg-black/60 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white text-xs font-semibold cursor-pointer"
                title="Change Athlete Picture"
              >
                <svg className="w-5 h-5 text-indigo-300 mb-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Upload
              </button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleProfilePicChange}
            />

            <div>
              <div className="flex items-center gap-3">
                <h3 className="text-xl sm:text-2xl font-bold text-white">
                  Athlete #{profile?.user_id || 3}
                </h3>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-400 font-medium">
                  {formData.position || "Left Back"}
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-medium flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Active Monitoring
                </span>
              </div>
              <p className="text-slate-400 text-sm mt-1">{userEmail || "athlete@sportsai.com"}</p>

              <div className="flex items-center gap-4 mt-2 text-xs">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-indigo-400 hover:text-indigo-300 font-medium underline underline-offset-2 transition-colors cursor-pointer"
                >
                  {profile?.profile_picture ? "Update Profile Photo" : "Add Profile Photo"}
                </button>
                {profile?.profile_picture && (
                  <>
                    <span className="text-slate-700">|</span>
                    <button
                      type="button"
                      onClick={handleRemoveProfilePic}
                      className="text-rose-400 hover:text-rose-300 font-medium transition-colors cursor-pointer"
                    >
                      Remove Photo
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link
              href="/dashboard/fitness"
              className="px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-semibold transition-all flex items-center gap-1.5"
            >
              <span>My Fitness</span> &rarr;
            </Link>
            <Link
              href="/dashboard/training"
              className="px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-semibold transition-all flex items-center gap-1.5"
            >
              <span>Training Plans</span> &rarr;
            </Link>
            <Link
              href="/dashboard/progress"
              className="px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-semibold transition-all flex items-center gap-1.5"
            >
              <span>Progress Log</span> &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800">
        {isEditing ? (
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Athlete Information Section */}
            <div>
              <h3 className="text-lg font-bold text-white mb-4 border-b border-slate-800 pb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Athlete Information
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Sport Type</label>
                  <input
                    required
                    type="text"
                    name="sport_type"
                    value={formData.sport_type}
                    onChange={handleChange}
                    placeholder="e.g. Football"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Position</label>
                  <input
                    required
                    type="text"
                    name="position"
                    value={formData.position}
                    onChange={handleChange}
                    placeholder="e.g. Left Back"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Age (Years)</label>
                  <input
                    required
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    placeholder="20"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Dominant Side / Foot</label>
                  <input
                    type="text"
                    name="dominant_side"
                    value={formData.dominant_side}
                    onChange={handleChange}
                    placeholder="e.g. Left Foot"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            {/* Physical Assessment Records Section */}
            <div>
              <h3 className="text-lg font-bold text-white mb-4 border-b border-slate-800 pb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Physical Assessment Records
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Height (cm)</label>
                  <input
                    required
                    type="number"
                    step="0.1"
                    name="height"
                    value={formData.height}
                    onChange={handleChange}
                    placeholder="170"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Weight (kg)</label>
                  <input
                    required
                    type="number"
                    step="0.1"
                    name="weight"
                    value={formData.weight}
                    onChange={handleChange}
                    placeholder="50"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Phone Number</label>
                  <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="+1 (555) 234-8901"
                    className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            {/* Training & History Management */}
            <div>
              <h3 className="text-lg font-bold text-white mb-4 border-b border-slate-800 pb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Training & History Management
              </h3>
              <div className="space-y-5">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Injury History Management</label>
                  <textarea
                    name="injury_history"
                    value={formData.injury_history}
                    onChange={handleChange}
                    rows={3}
                    placeholder="Describe any past injuries, bone cracks, surgeries, or chronic biomechanical vulnerabilities..."
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all resize-none"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-400">Training Profile & Load Management</label>
                  <textarea
                    name="training_load"
                    value={formData.training_load}
                    onChange={handleChange}
                    rows={3}
                    placeholder="Describe current training camps, weekly sessions, load parameters..."
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all resize-none"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-slate-400">Emergency & Physio Contact</label>
                    <input
                      type="text"
                      name="emergency_contact"
                      value={formData.emergency_contact}
                      onChange={handleChange}
                      placeholder="e.g. Dr. Marcus Vance (Physio) - +1 (555) 019-2834"
                      className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-slate-400">Personal Athletic Bio</label>
                    <input
                      type="text"
                      name="personal_bio"
                      value={formData.personal_bio}
                      onChange={handleChange}
                      placeholder="Short athletic summary or goals..."
                      className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm outline-none transition-all"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex items-center gap-4 pt-4 border-t border-slate-800">
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] disabled:opacity-50 text-sm cursor-pointer"
              >
                {saving ? "Saving Changes..." : "Save Athlete Profile"}
              </button>
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-xl border border-slate-700 text-sm transition-colors cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-8">
            {/* Athlete Information Cards */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                  Athlete Information
                </h3>
                <span className="text-xs text-slate-500">Verified Biometric File</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Athlete ID</div>
                  <div className="text-lg font-bold text-white mt-0.5">#{profile?.user_id || 3}</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Sport Type</div>
                  <div className="text-lg font-bold text-white mt-0.5">{profile?.sport_type || "Football"}</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Position</div>
                  <div className="text-lg font-bold text-white mt-0.5">{profile?.position || "Left Back"}</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Age</div>
                  <div className="text-lg font-bold text-white mt-0.5">{profile?.age || 20} yrs</div>
                </div>
              </div>
            </div>

            {/* Physical Assessment Records */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                  Physical Assessment Records
                </h3>
                <Link href="/dashboard/fitness" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
                  View Full Battery &rarr;
                </Link>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Height</div>
                  <div className="text-lg font-bold text-white mt-0.5">{profile?.height || 170} cm</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Weight</div>
                  <div className="text-lg font-bold text-white mt-0.5">{profile?.weight || 50} kg</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Body Mass Index (BMI)</div>
                  <div className="text-lg font-bold text-indigo-400 mt-0.5">{bmi} <span className="text-xs font-normal text-slate-400">kg/m²</span></div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/80">
                  <div className="text-xs text-slate-500">Performance Tracking</div>
                  <div className="text-emerald-400 font-semibold text-sm flex items-center gap-2 mt-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    Active monitoring enabled
                  </div>
                </div>
              </div>
            </div>

            {/* Training & History Management */}
            <div>
              <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                Training & History Management
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Injury History */}
                <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold uppercase text-slate-400 flex items-center gap-2">
                      <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Injury History Management
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
                      Under Clinical Attention
                    </span>
                  </div>
                  <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap pt-1 font-medium">
                    {profile?.injury_history || "Small bone cracks on right leg and recent crack on right leg small finger"}
                  </p>
                  <p className="text-[11px] text-slate-500 pt-2 border-t border-slate-800/60">
                    Targeted in Knee Valgus & Unilateral Romanian Deadlift protocols to prevent compensatory overloading.
                  </p>
                </div>

                {/* Training Profile Management */}
                <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold uppercase text-slate-400 flex items-center gap-2">
                      <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Training Profile Management
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                      High Load Intensity
                    </span>
                  </div>
                  <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap pt-1 font-medium">
                    {profile?.training_load || "Football camp"}
                  </p>
                  <p className="text-[11px] text-slate-500 pt-2 border-t border-slate-800/60">
                    Includes dynamic sprint acceleration, tactical small-sided matches, and scheduled regenerative recovery sessions.
                  </p>
                </div>
              </div>
            </div>

            {/* Additional Athletic Profile Details */}
            <div className="bg-slate-900/30 p-5 rounded-2xl border border-slate-800/60">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-sm">
                <div>
                  <div className="text-xs text-slate-500">Dominant Limb</div>
                  <div className="text-white font-medium mt-0.5">{profile?.dominant_side || "Left Foot (Left Back)"}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500">Emergency & Physio Contact</div>
                  <div className="text-white font-medium mt-0.5">{profile?.emergency_contact || "Dr. Marcus Vance - +1 (555) 019-2834"}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500">Contact Number</div>
                  <div className="text-white font-medium mt-0.5">{profile?.phone || "+1 (555) 234-8901"}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Connected Dashboard Navigation Links */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link
          href="/dashboard/fitness"
          className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all group"
        >
          <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 group-hover:text-indigo-300">
            Physical Assessments
          </div>
          <div className="text-white font-semibold text-sm">Review VO2 Max & FMS Scores &rarr;</div>
          <div className="text-xs text-slate-500 mt-1">Deep functional mobility battery and joint symmetry testing</div>
        </Link>

        <Link
          href="/dashboard/training"
          className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all group"
        >
          <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 group-hover:text-indigo-300">
            Training & Corrective
          </div>
          <div className="text-white font-semibold text-sm">Execute Prescribed Drills &rarr;</div>
          <div className="text-xs text-slate-500 mt-1">Knee valgus correction, core routines, and post-match recovery</div>
        </Link>

        <Link
          href="/dashboard/progress"
          className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all group"
        >
          <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 group-hover:text-indigo-300">
            Longitudinal Progress
          </div>
          <div className="text-white font-semibold text-sm">Track Valgus & Sprint Curves &rarr;</div>
          <div className="text-xs text-slate-500 mt-1">Multi-week velocity, deceleration angle, and workload trends</div>
        </Link>
      </div>
    </div>
  );
}
