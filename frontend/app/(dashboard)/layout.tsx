"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { getToken } from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { ShieldCheck } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, isLoading, error } = useAuth();

  // No token at all -> bounce immediately.
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!getToken()) {
      router.replace("/login");
    }
  }, [router]);

  // Auth error (e.g. token invalid) -> the api client already redirects on 401,
  // but cover the non-401 stale case here.
  useEffect(() => {
    if (error) router.replace("/login");
  }, [error, router]);

  if (isLoading || (!isAuthenticated && getToken())) {
    return <FullScreenLoader />;
  }

  if (!isAuthenticated) {
    return <FullScreenLoader />;
  }

  return <AppShell>{children}</AppShell>;
}

function FullScreenLoader() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas">
      <div className="flex flex-col items-center gap-3">
        <span className="inline-flex h-10 w-10 animate-pulse items-center justify-center rounded-xl bg-ai-gradient shadow-ai">
          <ShieldCheck className="h-5 w-5 text-white" aria-hidden />
        </span>
        <p className="text-sm text-slate-400">Loading your workspace…</p>
      </div>
    </div>
  );
}
