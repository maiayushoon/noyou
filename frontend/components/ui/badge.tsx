import { cn } from "@/lib/utils";

export type BadgeVariant =
  | "neutral"
  | "ai"
  | "success"
  | "warning"
  | "danger"
  | "outline";

const VARIANTS: Record<BadgeVariant, string> = {
  neutral: "bg-slate-100 text-slate-600",
  ai: "bg-ai-gradient text-white shadow-sm",
  success: "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200",
  warning: "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200",
  danger: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-200",
  outline: "border border-hairline text-slate-600",
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
