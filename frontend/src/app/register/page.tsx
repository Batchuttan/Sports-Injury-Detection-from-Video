"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function RegisterRedirectContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const email = searchParams.get("email");
    const target = email
      ? `/?mode=register&email=${encodeURIComponent(email)}`
      : "/?mode=register";
    router.replace(target);
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-300">
      <div className="flex items-center gap-3 p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-medium">Navigating to registration...</span>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950" />}>
      <RegisterRedirectContent />
    </Suspense>
  );
}

