"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AtSign, KeyRound, UserRound } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import { Button } from "@/components/ui/button";
import { FadeIn } from "@/components/motion/fade-in";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const toast = useToast();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.register({
        email: email.trim(),
        password,
        full_name: fullName.trim() || undefined,
      });
      // Auto sign-in for a smooth first run.
      await login(email.trim(), password);
      toast.success("Account created", "Welcome to NoYou.");
      router.replace("/");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Unable to create account. Please try again.";
      toast.error("Registration failed", message);
      setSubmitting(false);
    }
  }

  return (
    <FadeIn>
      <div className="mb-7">
        <h2 className="text-2xl font-semibold tracking-tight text-white">
          Create your account
        </h2>
        <p className="mt-1.5 text-sm text-slate-400">
          Start monitoring your reputation in minutes.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <Field
          id="full_name"
          label="Full name"
          type="text"
          placeholder="Ada Lovelace"
          autoComplete="name"
          icon={<UserRound className="h-4 w-4" />}
          value={fullName}
          onChange={setFullName}
        />
        <Field
          id="email"
          label="Email"
          type="email"
          placeholder="you@company.com"
          autoComplete="email"
          icon={<AtSign className="h-4 w-4" />}
          value={email}
          onChange={setEmail}
          required
        />
        <Field
          id="password"
          label="Password"
          type="password"
          placeholder="At least 8 characters"
          autoComplete="new-password"
          icon={<KeyRound className="h-4 w-4" />}
          value={password}
          onChange={setPassword}
          required
        />

        <Button
          type="submit"
          variant="ai"
          size="lg"
          loading={submitting}
          className="w-full"
        >
          Create account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-400">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-ai-indigo hover:underline">
          Sign in
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
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          {icon}
        </span>
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete={autoComplete}
          required={required}
          className="h-11 w-full rounded-lg border border-white/10 bg-white/[0.04] pl-10 pr-3 text-sm text-slate-100 outline-none transition-all duration-150 placeholder:text-slate-500 hover:border-white/20 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
        />
      </div>
    </div>
  );
}
