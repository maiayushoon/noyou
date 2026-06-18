"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, KeyRound, Loader2, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useToast } from "@/lib/toast";
import { FadeIn } from "@/components/motion/fade-in";

export default function ResetPasswordPage() {
  const router = useRouter();
  const toast = useToast();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") || "");
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      toast.error("Passwords do not match.");
      return;
    }
    setBusy(true);
    try {
      await api.resetPassword({ token, new_password: password });
      setDone(true);
      toast.success("Password updated. You can sign in now.");
      setTimeout(() => router.push("/login"), 1200);
    } catch {
      toast.error("This reset link is invalid or has expired.");
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <FadeIn>
        <div className="flex flex-col items-center text-center">
          <span className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600">
            <KeyRound className="h-6 w-6" aria-hidden />
          </span>
          <h2 className="text-xl font-semibold tracking-tight text-slate-900">Invalid reset link</h2>
          <p className="mt-1.5 max-w-xs text-sm text-slate-500">
            This link is missing its token. Request a new password reset to continue.
          </p>
          <Link href="/forgot-password" className="mt-6">
            <Button variant="ai" rightIcon={<ArrowRight className="h-4 w-4" />}>
              Request new link
            </Button>
          </Link>
        </div>
      </FadeIn>
    );
  }

  return (
    <FadeIn>
      <div className="mb-6">
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">Set a new password</h2>
        <p className="mt-1 text-sm text-slate-500">Choose a strong password you don&apos;t use anywhere else.</p>
      </div>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
            New password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/20"
            placeholder="At least 8 characters"
          />
        </div>
        <div>
          <label htmlFor="confirm" className="mb-1.5 block text-sm font-medium text-slate-700">
            Confirm password
          </label>
          <input
            id="confirm"
            type="password"
            required
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/20"
            placeholder="Re-enter your password"
          />
        </div>
        <Button
          type="submit"
          variant="ai"
          className="w-full"
          disabled={busy || done}
          leftIcon={
            done ? (
              <ShieldCheck className="h-4 w-4" />
            ) : busy ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <KeyRound className="h-4 w-4" />
            )
          }
        >
          {done ? "Password updated" : busy ? "Updating…" : "Update password"}
        </Button>
      </form>
    </FadeIn>
  );
}
