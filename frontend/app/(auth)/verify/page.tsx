"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, CheckCircle2, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { FadeIn } from "@/components/motion/fade-in";

export default function VerifyEmailPage() {
  const [state, setState] = useState<"loading" | "ok" | "error">("loading");
  const [message, setMessage] = useState("Verifying your email…");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) {
      setState("error");
      setMessage("No verification token found in the link.");
      return;
    }
    api
      .verifyEmail({ token })
      .then((r) => {
        setState("ok");
        setMessage(r.message || "Your email is verified. You can now sign in.");
      })
      .catch(() => {
        setState("error");
        setMessage("This verification link is invalid or has expired.");
      });
  }, []);

  return (
    <FadeIn>
      <div className="flex flex-col items-center text-center">
        <span
          className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl ring-1 ring-inset ${
            state === "ok"
              ? "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30"
              : state === "error"
              ? "bg-red-500/15 text-red-300 ring-red-500/30"
              : "bg-ai-indigo/15 text-amber-200 ring-white/[0.08]"
          }`}
        >
          {state === "loading" ? (
            <Loader2 className="h-6 w-6 animate-spin" aria-hidden />
          ) : state === "ok" ? (
            <CheckCircle2 className="h-6 w-6" aria-hidden />
          ) : (
            <AlertTriangle className="h-6 w-6" aria-hidden />
          )}
        </span>
        <h2 className="text-xl font-semibold tracking-tight text-white">
          {state === "ok" ? "Email verified" : state === "error" ? "Verification failed" : "Verifying…"}
        </h2>
        <p className="mt-1.5 max-w-xs text-sm text-slate-400">{message}</p>
        {state !== "loading" ? (
          <Link href="/login" className="mt-6">
            <Button variant="ai" rightIcon={<ArrowRight className="h-4 w-4" />}>
              Go to sign in
            </Button>
          </Link>
        ) : null}
      </div>
    </FadeIn>
  );
}
