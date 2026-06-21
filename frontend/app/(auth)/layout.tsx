import { ShieldCheck } from "lucide-react";
import { BrandPanel } from "@/components/auth/brand-panel";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Left brand panel — animated 3D showcase (dark, AI gradient accents) */}
      <BrandPanel />

      {/* Right form panel */}
      <div className="flex items-center justify-center bg-canvas px-6 py-12">
        <div className="w-full max-w-sm">
          {/* Mobile-only brand mark (brand panel is hidden below lg) */}
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-ai-gradient shadow-ai">
              <ShieldCheck className="h-5 w-5 text-white" aria-hidden />
            </span>
            <span className="text-lg font-semibold tracking-tight text-slate-900">
              NoYou
            </span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
