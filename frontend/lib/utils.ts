import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind classes with conflict resolution. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Compact relative time, e.g. "3m ago", "2d ago". */
export function timeAgo(input: string | number | Date | null | undefined): string {
  if (!input) return "—";
  const date = input instanceof Date ? input : new Date(input);
  const ts = date.getTime();
  if (Number.isNaN(ts)) return "—";

  const seconds = Math.round((Date.now() - ts) / 1000);
  if (seconds < 45) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 7) return `${days}d ago`;
  const weeks = Math.round(days / 7);
  if (weeks < 5) return `${weeks}w ago`;
  const months = Math.round(days / 30);
  if (months < 12) return `${months}mo ago`;
  const years = Math.round(days / 365);
  return `${years}y ago`;
}

/** Absolute, readable date. */
export function formatDate(input: string | number | Date | null | undefined): string {
  if (!input) return "—";
  const date = input instanceof Date ? input : new Date(input);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export type ScoreBand = "low" | "medium" | "high" | "excellent" | "critical";
export type Sentiment = "positive" | "neutral" | "negative";

/**
 * Band color helper. The dashboard band is (low|medium|high|critical),
 * AI visibility band is (low|medium|high|excellent). Both share keys.
 */
export function bandColor(band: ScoreBand | string): {
  text: string;
  bg: string;
  ring: string;
  dot: string;
  label: string;
} {
  switch (band) {
    case "excellent":
      return {
        text: "text-emerald-300",
        bg: "bg-emerald-500/15",
        ring: "ring-emerald-500/30",
        dot: "bg-emerald-400",
        label: "Excellent",
      };
    case "high":
      return {
        text: "text-emerald-300",
        bg: "bg-emerald-500/15",
        ring: "ring-emerald-500/30",
        dot: "bg-emerald-400",
        label: "Strong",
      };
    case "medium":
      return {
        text: "text-amber-300",
        bg: "bg-amber-500/15",
        ring: "ring-amber-500/30",
        dot: "bg-amber-400",
        label: "Fair",
      };
    case "low":
      return {
        text: "text-orange-300",
        bg: "bg-orange-500/15",
        ring: "ring-orange-500/30",
        dot: "bg-orange-400",
        label: "At risk",
      };
    case "critical":
      return {
        text: "text-red-300",
        bg: "bg-red-500/15",
        ring: "ring-red-500/30",
        dot: "bg-red-400",
        label: "Critical",
      };
    default:
      return {
        text: "text-slate-300",
        bg: "bg-white/[0.06]",
        ring: "ring-white/[0.10]",
        dot: "bg-slate-400",
        label: "Unknown",
      };
  }
}

export function sentimentColor(sentiment: Sentiment | string): {
  text: string;
  bg: string;
  border: string;
  dot: string;
  hex: string;
  label: string;
} {
  switch (sentiment) {
    case "positive":
      return {
        text: "text-emerald-300",
        bg: "bg-emerald-500/15",
        border: "border-emerald-500/30",
        dot: "bg-emerald-400",
        hex: "#10b981",
        label: "Positive",
      };
    case "negative":
      return {
        text: "text-red-300",
        bg: "bg-red-500/15",
        border: "border-red-500/30",
        dot: "bg-red-400",
        hex: "#ef4444",
        label: "Negative",
      };
    case "neutral":
    default:
      return {
        text: "text-slate-300",
        bg: "bg-white/[0.06]",
        border: "border-white/[0.10]",
        dot: "bg-slate-400",
        hex: "#64748b",
        label: "Neutral",
      };
  }
}

/** Risk level 0-5 color + label. */
export function riskColor(level: number): {
  text: string;
  bg: string;
  border: string;
  dot: string;
  hex: string;
  label: string;
} {
  if (level >= 4) {
    return {
      text: "text-red-300",
      bg: "bg-red-500/15",
      border: "border-red-500/30",
      dot: "bg-red-400",
      hex: "#ef4444",
      label: "Critical",
    };
  }
  if (level >= 3) {
    return {
      text: "text-orange-300",
      bg: "bg-orange-500/15",
      border: "border-orange-500/30",
      dot: "bg-orange-400",
      hex: "#f97316",
      label: "High",
    };
  }
  if (level >= 2) {
    return {
      text: "text-amber-300",
      bg: "bg-amber-500/15",
      border: "border-amber-500/30",
      dot: "bg-amber-400",
      hex: "#f59e0b",
      label: "Medium",
    };
  }
  if (level >= 1) {
    return {
      text: "text-yellow-300",
      bg: "bg-yellow-500/15",
      border: "border-yellow-500/30",
      dot: "bg-yellow-400",
      hex: "#eab308",
      label: "Low",
    };
  }
  return {
    text: "text-slate-300",
    bg: "bg-white/[0.06]",
    border: "border-white/[0.10]",
    dot: "bg-slate-400",
    hex: "#64748b",
    label: "Minimal",
  };
}

/** Severity (alerts) color + label. */
export function severityColor(severity: string): {
  text: string;
  bg: string;
  border: string;
  dot: string;
  label: string;
} {
  switch (severity) {
    case "critical":
      return { text: "text-red-300", bg: "bg-red-500/15", border: "border-red-500/30", dot: "bg-red-400", label: "Critical" };
    case "high":
      return { text: "text-orange-300", bg: "bg-orange-500/15", border: "border-orange-500/30", dot: "bg-orange-400", label: "High" };
    case "medium":
      return { text: "text-amber-300", bg: "bg-amber-500/15", border: "border-amber-500/30", dot: "bg-amber-400", label: "Medium" };
    case "low":
    default:
      return { text: "text-slate-300", bg: "bg-white/[0.06]", border: "border-white/[0.10]", dot: "bg-slate-400", label: "Low" };
  }
}

/** Title-case a snake/kebab token, e.g. "do_not_post" -> "Do Not Post". */
export function humanize(value: string | null | undefined): string {
  if (!value) return "";
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Clamp a number into [min, max]. */
export function clamp(value: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, value));
}
