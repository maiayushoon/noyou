import { Minus, ThumbsDown, ThumbsUp } from "lucide-react";
import { sentimentColor, type Sentiment } from "@/lib/utils";
import { cn } from "@/lib/utils";

const ICONS = {
  positive: ThumbsUp,
  negative: ThumbsDown,
  neutral: Minus,
} as const;

export function SentimentBadge({
  sentiment,
  showLabel = true,
  className,
}: {
  sentiment: Sentiment | string;
  showLabel?: boolean;
  className?: string;
}) {
  const c = sentimentColor(sentiment);
  const Icon = ICONS[(sentiment as Sentiment) in ICONS ? (sentiment as keyof typeof ICONS) : "neutral"];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium",
        c.bg,
        c.text,
        c.border,
        className
      )}
    >
      <Icon className="h-3 w-3" aria-hidden />
      {showLabel ? c.label : null}
    </span>
  );
}
