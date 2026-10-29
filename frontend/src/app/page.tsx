"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { login, register, googleLogin, forgotPassword } from "@/lib/api";
import { useGoogleLogin } from "@react-oauth/google";

export default function Home() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("demo@sportsai.com");
  const [password, setPassword] = useState("password123");
  const [role, setRole] = useState("Athlete");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Forgot password modal state
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotSuccess, setForgotSuccess] = useState("");
  const [forgotError, setForgotError] = useState("");

  const router = useRouter();

  useEffect(() => {
    // Prefetch dashboard route in background for instantaneous sign-in transition
    router.prefetch("/dashboard");
  }, [router]);

  const googleLoginHook = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setLoading(true);
      setError("");
      try {
        // We get an access token from Google, but usually we need user info.
        // For simplicity, we can fetch user info from Google API here
        const res = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        });
        const userInfo = await res.json();

        if (!userInfo.email) {
          throw new Error("Could not get email from Google");
        }

        const data = await googleLogin(userInfo.email, role);
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      } catch (err) {
        console.error(err);
        setError("Google Login failed");
      } finally {
        setLoading(false);
      }
    },
    onError: () => {
      setError("Google Login was cancelled or failed");
    }
  });

  const handleGoogleAuth = async () => {
    googleLoginHook();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isLogin) {
        const data = await login(email, password);
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      } else {
        await register(email, password, role);
        const data = await login(email, password);
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      }
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.toLowerCase().includes("failed to fetch")) {
          setError("Cannot connect to server. Please ensure the backend is running.");
        } else {
          setError(err.message || "An error occurred. Please try again.");
        }
      } else {
        setError("An error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotError("");
    setForgotSuccess("");

    if (!forgotEmail || !forgotEmail.includes("@")) {
      setForgotError("Please enter a valid email address.");
      return;
    }

    setForgotLoading(true);
    try {
      const res = await forgotPassword(forgotEmail);
      setForgotSuccess(res.message || "A secure password reset link has been dispatched to your email address!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to dispatch reset email. Please try again.";
      setForgotError(msg);
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <main className="flex-grow flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-600/20 blur-[120px] pointer-events-none transform-gpu" style={{ willChange: "transform" }} />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-pink-600/20 blur-[120px] pointer-events-none transform-gpu" style={{ willChange: "transform" }} />

      <div className="z-10 w-full max-w-5xl px-6 py-20 flex flex-col md:flex-row items-center gap-12">

        {/* Left column: Hero content */}
        <div className="flex-1 space-y-8 text-center md:text-left">
          <div className="inline-block px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium tracking-wide">
            AI-Powered Biomechanics
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
            Predict &amp; Prevent <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-500">
              Sports Injuries
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-xl mx-auto md:mx-0">
            Advanced pose estimation and biomechanical analysis to identify risks before injuries happen. Trusted by top athletes, coaches, and medical teams.
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-4 pt-4 justify-center md:justify-start">
            <Link
              href="/dashboard"
              className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-all shadow-[0_0_20px_rgba(79,70,229,0.4)] hover:shadow-[0_0_30px_rgba(79,70,229,0.6)] hover:-translate-y-0.5 w-full sm:w-auto text-center"
            >
              Enter Dashboard
            </Link>
            <button className="px-8 py-4 rounded-xl border border-slate-700 hover:border-slate-500 bg-slate-800/50 hover:bg-slate-800 text-white font-medium transition-all w-full sm:w-auto">
              View Demo
            </button>
          </div>
        </div>

        {/* Right column: Login / Feature card */}
        <div className="flex-1 w-full max-w-md">
          <div className="glass-panel p-8 rounded-2xl relative group">
            <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl pointer-events-none" />

            <div className="relative z-10 space-y-6">
              <div className="text-center">
                <h3 className="text-2xl font-bold text-white mb-2">{isLogin ? "Platform Access" : "Create Account"}</h3>
                <p className="text-slate-400 text-sm">{isLogin ? "Sign in to your intelligent sports hub" : "Join the sports injury prevention platform"}</p>
              </div>

              <form className="space-y-4" onSubmit={handleSubmit}>
                {error && <div className="text-rose-500 text-sm font-medium">{error}</div>}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-300">Email Address</label>
                  <input
                    type="email"
                    placeholder="coach@team.com"
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-slate-100 placeholder:text-slate-600"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-300">Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-slate-100 placeholder:text-slate-600"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 text-sm font-medium"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                </div>

                {!isLogin && (
                  <div className="space-y-1">
                    <label className="text-sm font-medium text-slate-300">Role</label>
                    <select
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-slate-100 appearance-none"
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                    >
                      <option value="Athlete">Athlete</option>
                      <option value="Coach">Coach</option>
                      <option value="Physiotherapist">Physiotherapist</option>
                      <option value="Sports Scientist">Sports Scientist</option>
                      <option value="Administrator">Administrator</option>
                    </select>
                  </div>
                )}

                {isLogin && (
                  <div className="flex items-center justify-between text-sm">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" className="rounded border-slate-700 bg-slate-900/50 text-indigo-500 focus:ring-indigo-500/30" />
                      <span className="text-slate-400">Remember me</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        setForgotEmail(email);
                        setForgotError("");
                        setForgotSuccess("");
                        setShowForgotModal(true);
                      }}
                      className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
                    >
                      Forgot password?
                    </button>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="block w-full py-3 px-4 bg-white text-slate-900 text-center font-bold rounded-xl hover:bg-slate-200 transition-colors mt-6 disabled:opacity-50"
                >
                  {loading ? (isLogin ? "Signing In..." : "Creating Account...") : (isLogin ? "Sign In ->" : "Sign Up ->")}
                </button>

                <div className="mt-4 flex items-center justify-between">
                  <hr className="w-full border-slate-700" />
                  <span className="px-3 text-slate-400 text-sm">or</span>
                  <hr className="w-full border-slate-700" />
                </div>

                <button
                  type="button"
                  onClick={handleGoogleAuth}
                  className="w-full py-3 px-4 bg-slate-800 border border-slate-700 text-white font-semibold rounded-xl hover:bg-slate-700 transition-colors flex items-center justify-center gap-3 mt-4"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  {isLogin ? "Sign In with Google" : "Register with Google"}
                </button>
              </form>

              <div className="text-center mt-4">
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  {isLogin ? "Need an account? Register" : "Already have an account? Sign in"}
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-md glass-panel bg-slate-900/95 border border-slate-700/80 rounded-3xl p-7 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.8),0_0_30px_rgba(79,70,229,0.15)] relative overflow-hidden">
            {/* Top accent gradient bar */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

            <button
              onClick={() => setShowForgotModal(false)}
              className="absolute right-4 top-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
              aria-label="Close dialog"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {forgotSuccess ? (
              /* Success View - Directs user strictly to check their external email inbox */
              <div className="pt-2 text-center space-y-5 animate-fadeIn">
                <div className="relative mx-auto w-16 h-16 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full bg-emerald-500/20 blur-md animate-pulse" />
                  <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-600/30 to-teal-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center shadow-lg">
                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center text-slate-950">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-extrabold text-white">Reset Link Dispatched</h3>
                  <p className="text-slate-400 text-xs mt-1">
                    Please check your mailbox to continue
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 text-left space-y-2.5">
                  <p className="text-xs text-slate-300 leading-relaxed">
                    We sent an official password reset email to:
                  </p>
                  <div className="px-3 py-2 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-center">
                    <span className="font-semibold text-indigo-300 text-sm break-all">{forgotEmail}</span>
                  </div>
                  <div className="pt-1 flex items-start gap-2 text-[11px] text-slate-400 leading-snug">
                    <svg className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>
                      Open your email provider and click the button or link inside. The link is secure and valid for <strong>30 minutes</strong>.
                    </span>
                  </div>
                </div>

                <div className="pt-2 space-y-2.5">
                  <button
                    type="button"
                    onClick={() => setShowForgotModal(false)}
                    className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm transition-all shadow-[0_0_20px_rgba(79,70,229,0.35)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)]"
                  >
                    Return to Sign In
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setForgotSuccess("");
                      setForgotError("");
                    }}
                    className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    Entered wrong email? Try again
                  </button>
                </div>
              </div>
            ) : (
              /* Email Input Form */
              <div className="pt-1 space-y-5">
                <div className="text-center">
                  <div className="w-12 h-12 bg-indigo-500/15 text-indigo-400 rounded-2xl flex items-center justify-center mx-auto mb-3 border border-indigo-500/30 shadow-[0_0_20px_rgba(79,70,229,0.2)]">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-extrabold text-white">Reset Account Password</h3>
                  <p className="text-slate-400 text-xs mt-1 max-w-sm mx-auto leading-relaxed">
                    Provide the email associated with your account. A secure password reset link will be sent to your inbox.
                  </p>
                </div>

                {forgotError && (
                  <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                    <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{forgotError}</span>
                  </div>
                )}

                <form onSubmit={handleForgotSubmit} className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <svg className="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.206" />
                      </svg>
                      Account Email
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="athlete@team.com"
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-950/80 border border-slate-700/80 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 placeholder:text-slate-600 text-sm transition-all"
                      autoFocus
                    />
                  </div>

                  <div className="pt-2 flex gap-3">
                    <button
                      type="button"
                      onClick={() => setShowForgotModal(false)}
                      className="flex-1 py-3 px-4 bg-slate-800/80 hover:bg-slate-800 text-slate-300 font-semibold rounded-xl text-sm transition-colors border border-slate-700"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={forgotLoading}
                      className="flex-1 py-3 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold rounded-xl text-sm transition-all shadow-[0_0_15px_rgba(79,70,229,0.4)] hover:shadow-[0_0_20px_rgba(79,70,229,0.6)] flex items-center justify-center gap-2"
                    >
                      {forgotLoading ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Dispatching...</span>
                        </>
                      ) : (
                        <span>Send Link</span>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
