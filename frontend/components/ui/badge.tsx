import { cn } from "@/lib/utils";

export type BadgeVariant =
  | "neutral"
  | "ai"
  | "success"
  | "warning"
  | "danger"
  | "outline";

const VARIANTS: Record<BadgeVariant, string> = {
  neutral: "bg-white/[0.06] text-slate-300",
  ai: "bg-ai-gradient text-white shadow-sm",
  success:
    "bg-emerald-500/15 text-emerald-300 ring-1 ring-inset ring-emerald-500/30",
  warning: "bg-amber-500/15 text-amber-300 ring-1 ring-inset ring-amber-500/30",
  danger: "bg-red-500/15 text-red-300 ring-1 ring-inset ring-red-500/30",
  outline: "border border-white/[0.12] text-slate-300",
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  dot?: boolean;
  dotClassName?: string;
}

export function Badge({
  className,
  variant = "neutral",
  dot = false,
  dotClassName,
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        VARIANTS[variant],
        className
      )}
      {...props}
    >
      {dot ? (
        <span
          className={cn("h-1.5 w-1.5 rounded-full", dotClassName ?? "bg-current")}
          aria-hidden
        />
      ) : null}
      {children}
    </span>
  );
}
