import { ShieldAlert, ShieldCheck } from "lucide-react";
import { riskColor } from "@/lib/utils";
import { cn } from "@/lib/utils";

export function RiskBadge({
  level,
  showLevel = true,
  className,
}: {
  level: number;
  showLevel?: boolean;
  className?: string;
}) {
  const c = riskColor(level);
  const Icon = level >= 3 ? ShieldAlert : ShieldCheck;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium",
        c.bg,
        c.text,
        c.border,
        className
      )}
      title={`Risk level ${level} of 5`}
    >
      <Icon className="h-3 w-3" aria-hidden />
      {c.label}
      {showLevel ? <span className="opacity-60">· {level}/5</span> : null}
    </span>
  );
}
