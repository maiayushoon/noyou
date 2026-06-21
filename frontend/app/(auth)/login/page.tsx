"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AtSign, KeyRound, Sparkles } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { FadeIn } from "@/components/motion/fade-in";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(email.trim(), password);
      toast.success("Welcome back");
      router.replace("/");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Unable to sign in. Please try again.";
      toast.error("Sign in failed", message);
      setSubmitting(false);
    }
  }

  return (
    <FadeIn>
      <div className="mb-7">
        <h2 className="text-2xl font-semibold tracking-tight text-white">
          Sign in
        </h2>
        <p className="mt-1.5 text-sm text-slate-400">
          Welcome back. Enter your details to continue.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <Field
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@company.com"
          icon={<AtSign className="h-4 w-4" />}
          value={email}
          onChange={setEmail}
          required
        />
        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <label htmlFor="password" className="text-sm font-medium text-slate-300">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-xs font-medium text-ai-indigo hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <InputShell icon={<KeyRound className="h-4 w-4" />}>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="h-11 w-full rounded-lg border border-white/10 bg-white/[0.04] pl-10 pr-3 text-sm text-slate-100 outline-none transition-all duration-150 placeholder:text-slate-500 hover:border-white/20 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
            />
          </InputShell>
        </div>

        <Button
          type="submit"
          variant="ai"
          size="lg"
          loading={submitting}
          className="w-full"
        >
          Sign in
        </Button>
      </form>

      <div className="mt-5 rounded-lg border border-white/[0.08] bg-white/[0.03] p-3 text-xs text-slate-400">
        <span className="inline-flex items-center gap-1.5 font-medium text-slate-300">
          <Sparkles className="h-3.5 w-3.5 text-ai-violet" aria-hidden />
          Demo access
        </span>
        <p className="mt-1">
          Use{" "}
          <code className="rounded bg-white/[0.08] px-1 py-0.5 text-slate-200">
            demo@noyou.app
          </code>{" "}
          /{" "}
          <code className="rounded bg-white/[0.08] px-1 py-0.5 text-slate-200">
            demo12345
          </code>
        </p>
      </div>

      <p className="mt-6 text-center text-sm text-slate-400">
        No account?{" "}
        <Link
          href="/register"
          className="font-medium text-ai-indigo hover:underline"
        >
          Create one
        </Link>
      </p>
    </FadeIn>
  );
}

function Field({
  id,
  label,
  type,
  placeholder,
  value,
  onChange,
  icon,
  autoComplete,
  required,
}: {
  id: string;
  label: string;
  type: string;
  placeholder?: string;
  value: string;
  onChange: (v: string) => void;
  icon: React.ReactNode;
  autoComplete?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-slate-300">
        {label}
      </label>
      <InputShell icon={icon}>
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete={autoComplete}
          required={required}
          className="h-11 w-full rounded-lg border border-white/10 bg-white/[0.04] pl-10 pr-3 text-sm text-slate-100 outline-none transition-colors placeholder:text-slate-500 hover:border-white/20 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
        />
      </InputShell>
    </div>
  );
}

function InputShell({
  icon,
  children,
}: {
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="relative">
      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
        {icon}
      </span>
      {children}
    </div>
  );
}
