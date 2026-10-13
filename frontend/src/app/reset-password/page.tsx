"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { verifyResetToken, resetPassword } from "@/lib/api";

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const token = searchParams.get("token") || "";
  const mode = searchParams.get("mode") || "reset"; // 'reset' or 'change'

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const [tokenValid, setTokenValid] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (!token) {
      setErrorMessage("No password reset token provided. Please use the link sent to your email.");
      setLoading(false);
      return;
    }

    const checkToken = async () => {
      try {
        const res = await verifyResetToken(token);
        setTokenValid(true);
        setUserEmail(res.email || "");
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Invalid or expired password reset link.";
        setErrorMessage(msg);
      } finally {
        setLoading(false);
      }
    };

    checkToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (password.length < 6) {
      setErrorMessage("Password must be at least 6 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match. Please re-enter.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await resetPassword(token, password);
      setSuccessMessage(res.message || "Password updated successfully!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update password.";
      setErrorMessage(msg);
    } finally {
      setSubmitting(false);
    }
  };

  // Password strength helper
  const getPasswordStrength = () => {
    if (!password) return { score: 0, label: "Too Short", color: "bg-slate-700" };
    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 10) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    if (score <= 1) return { score: 1, label: "Weak", color: "bg-rose-500" };
    if (score <= 3) return { score: 2, label: "Medium", color: "bg-amber-500" };
    return { score: 3, label: "Strong", color: "bg-emerald-500" };
  };

  const strength = getPasswordStrength();

  return (
    <main className="min-h-screen bg-slate-950 flex flex-col items-center justify-center relative p-6 overflow-hidden">
      {/* Background glow decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[45%] h-[45%] rounded-full bg-indigo-600/15 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[45%] h-[45%] rounded-full bg-pink-600/15 blur-[120px]" />

      <div className="z-10 w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <span className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-500 tracking-tight">
              SportsAI
            </span>
          </Link>
          <div className="text-xs text-slate-500 uppercase tracking-widest mt-1 font-semibold">
            Biomechanical Security Hub
          </div>
        </div>

        <div className="glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl relative">
          {loading ? (
            <div className="py-12 text-center space-y-4">
              <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-slate-400 text-sm">Verifying security token...</p>
            </div>
          ) : successMessage ? (
            <div className="text-center py-6 space-y-5">
              <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">Password Successfully Updated!</h3>
                <p className="text-slate-400 text-sm">
                  Your credentials have been securely refreshed. You can now access your SportsAI account with your new password.
                </p>
              </div>
              <button
                onClick={() => router.push("/")}
                className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)]"
              >
                Go to Sign In &rarr;
              </button>
            </div>
          ) : !tokenValid ? (
            <div className="text-center py-6 space-y-5">
              <div className="w-16 h-16 bg-rose-500/20 text-rose-400 rounded-full flex items-center justify-center mx-auto border border-rose-500/30">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">Link Expired or Invalid</h3>
                <p className="text-slate-400 text-sm">
                  {errorMessage || "This security link has expired or has already been used. Password reset links are valid for 30 minutes."}
                </p>
              </div>
              <div className="pt-2 flex flex-col gap-3">
                <Link
                  href="/"
                  className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-xl transition-colors text-sm text-center"
                >
                  Return to Sign In
                </Link>
              </div>
            </div>
          ) : (
            <div>
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-1">
                  {mode === "change" ? "Confirm New Password" : "Reset Your Password"}
                </h3>
                <p className="text-slate-400 text-sm">
                  {userEmail ? (
                    <>
                      Updating credentials for <span className="text-indigo-400 font-medium">{userEmail}</span>
                    </>
                  ) : (
                    "Choose a strong, secure new password"
                  )}
                </p>
              </div>

              {errorMessage && (
                <div className="p-3 mb-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
                  {errorMessage}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      placeholder="Enter new password (min. 6 chars)"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900/60 border border-slate-700 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 placeholder:text-slate-600 text-sm pr-11"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs px-1"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                </div>

                {/* Password strength indicator */}
                {password.length > 0 && (
                  <div className="space-y-1 pt-1">
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>Strength</span>
                      <span className="font-medium text-slate-300">{strength.label}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1.5 h-1.5">
                      <div className={`rounded-full ${strength.score >= 1 ? strength.color : "bg-slate-800"}`} />
                      <div className={`rounded-full ${strength.score >= 2 ? strength.color : "bg-slate-800"}`} />
                      <div className={`rounded-full ${strength.score >= 3 ? strength.color : "bg-slate-800"}`} />
                    </div>
                  </div>
                )}

                <div className="space-y-1 pt-1">
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Confirm New Password
                  </label>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    placeholder="Repeat new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/60 border border-slate-700 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 placeholder:text-slate-600 text-sm"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)] flex items-center justify-center gap-2"
                  >
                    {submitting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Saving Password...
                      </>
                    ) : (
                      "Update Password"
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        <div className="text-center mt-6">
          <Link href="/" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">
            &larr; Back to Platform Access
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
          Loading security portal...
        </div>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
