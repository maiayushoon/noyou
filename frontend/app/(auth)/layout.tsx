import { ShieldCheck, Sparkles } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Left brand panel (dark, AI gradient accents) */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-sidebar p-12 lg:flex">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-ai-gradient opacity-30 blur-3xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-ai-gradient opacity-20 blur-3xl"
          aria-hidden
        />
        <div className="relative flex items-center gap-2.5">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-ai-gradient shadow-ai">
            <ShieldCheck className="h-5 w-5 text-white" aria-hidden />
          </span>
          <span className="text-lg font-semibold tracking-tight text-white">
            NoYou
          </span>
        </div>

        <div className="relative max-w-md">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-slate-200">
            <Sparkles className="h-3.5 w-3.5" aria-hidden />
            AI reputation intelligence
          </span>
          <h1 className="mt-5 text-3xl font-semibold leading-tight tracking-tight text-white">
            Know what the internet —{" "}
            <span className="text-gradient-ai">and AI</span> — says about you.
          </h1>
          <p className="mt-4 text-[0.95rem] leading-relaxed text-slate-400">
            NoYou monitors mentions across the web, scores your reputation in
            real time, and recommends exactly what to clean up next.
          </p>
        </div>

        <p className="relative text-xs text-slate-500">
          © {new Date().getFullYear()} NoYou. Your reputation, protected.
        </p>
      </div>

      {/* Right form panel */}
      <div className="flex items-center justify-center bg-canvas px-6 py-12">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}
