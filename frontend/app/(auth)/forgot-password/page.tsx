"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, AtSign, MailCheck } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/lib/toast";
import { Button } from "@/components/ui/button";
import { FadeIn } from "@/components/motion/fade-in";

export default function ForgotPasswordPage() {
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.forgotPassword({ email: email.trim() });
      setSent(true);
    } catch (err) {
      // Backend may intentionally return success regardless; show generic confirmation.
      if (err instanceof ApiError && err.status >= 500) {
        toast.error("Something went wrong", "Please try again shortly.");
      } else {
        setSent(true);
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (sent) {
    return (
      <FadeIn>
        <div className="flex flex-col items-center text-center">
          <span className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-300 ring-1 ring-inset ring-emerald-500/30">
            <MailCheck className="h-6 w-6" aria-hidden />
          </span>
          <h2 className="text-xl font-semibold tracking-tight text-white">
            Check your inbox
          </h2>
          <p className="mt-1.5 max-w-xs text-sm text-slate-400">
            If an account exists for {email || "that address"}, we sent a link to
            reset your password.
          </p>
          <Link href="/login" className="mt-6">
            <Button variant="outline" leftIcon={<ArrowLeft className="h-4 w-4" />}>
              Back to sign in
            </Button>
          </Link>
        </div>
      </FadeIn>
    );
  }

  return (
    <FadeIn>
      <div className="mb-7">
        <h2 className="text-2xl font-semibold tracking-tight text-white">
          Reset your password
        </h2>
        <p className="mt-1.5 text-sm text-slate-400">
          Enter your email and we&apos;ll send a reset link.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-300">
            Email
          </label>
          <div className="relative">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              <AtSign className="h-4 w-4" />
            </span>
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="h-11 w-full rounded-lg border border-white/10 bg-white/[0.04] pl-10 pr-3 text-sm text-slate-100 outline-none transition-colors placeholder:text-slate-500 hover:border-white/20 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
            />
          </div>
        </div>

        <Button type="submit" variant="ai" size="lg" loading={submitting} className="w-full">
          Send reset link
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-400">
        <Link href="/login" className="font-medium text-ai-indigo hover:underline">
          Back to sign in
        </Link>
      </p>
    </FadeIn>
  );
}
