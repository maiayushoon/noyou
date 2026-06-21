"use client";

import useSWR from "swr";
import {
  ArrowRight,
  Check,
  Lightbulb,
  Minus,
  Sparkles,
} from "lucide-react";
import { api, type AiVisibility } from "@/lib/api";
import { bandColor, cn } from "@/lib/utils";
import {
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  PlanGate,
  ScoreRing,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn } from "@/components/motion/fade-in";

export default function AiVisibilityPage() {
  const { data, error, isLoading } = useSWR<AiVisibility>(
    "ai-visibility",
    () => api.aiVisibility(),
    { shouldRetryOnError: false }
  );

  return (
    <div>
      <PageHeader
        title="AI Visibility"
        description="How AI engines like ChatGPT and Gemini describe your brand — and how to improve that signal."
        actions={
          <Badge variant="ai" dot dotClassName="bg-white">
            AI
          </Badge>
        }
      />

      <PlanGate error={error} feature="ai_visibility">
        {isLoading || !data ? (
          <Skeletons />
        ) : (
          <div className="space-y-6">
            <FadeIn>
              <Card className="overflow-hidden">
                <div className="grid gap-6 p-6 md:grid-cols-[auto,1fr] md:items-center md:gap-10">
                  <div className="flex justify-center md:justify-start">
                    <ScoreRing
                      score={data.ai_visibility_score}
                      label={bandColor(data.band).label}
                    />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-ai-violet" aria-hidden />
                      <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                        AI visibility · {data.brand}
                      </span>
                    </div>
                    <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white">
                      {data.summary}
                    </h2>
                    <p className="mt-2 text-xs text-slate-400">
                      Assessed via {data.llm_used}
                    </p>
                  </div>
                </div>
              </Card>
            </FadeIn>

            <div className="grid gap-6 lg:grid-cols-2">
              <FadeIn delay={0.05}>
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle>Signals AI engines look for</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2.5">
                    {data.signals.map((s) => (
                      <div
                        key={s.name}
                        className="flex items-start gap-3 rounded-lg border border-white/[0.08] bg-white/[0.02] p-3"
                      >
                        <span
                          className={cn(
                            "mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full",
                            s.present
                              ? "bg-emerald-500/15 text-emerald-300 ring-1 ring-inset ring-emerald-500/30"
                              : "bg-white/[0.06] text-slate-400"
                          )}
                          aria-hidden
                        >
                          {s.present ? (
                            <Check className="h-3.5 w-3.5" />
                          ) : (
                            <Minus className="h-3.5 w-3.5" />
                          )}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-sm font-medium text-slate-100">
                              {s.name}
                            </p>
                            <span className="shrink-0 text-xs text-slate-400">
                              weight {s.weight}
                            </span>
                          </div>
                          <p className="mt-0.5 text-sm text-slate-400">{s.detail}</p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </FadeIn>

              <FadeIn delay={0.1}>
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle>Recommended next steps</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {data.recommendations.length === 0 ? (
                      <p className="text-sm text-slate-400">
                        You&apos;re covering the fundamentals. Keep publishing
                        authoritative, consistent content.
                      </p>
                    ) : (
                      <ol className="space-y-3">
                        {data.recommendations.map((r, i) => (
                          <li key={i} className="flex items-start gap-3">
                            <span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ai-gradient-soft text-amber-200 ring-1 ring-inset ring-white/[0.08]">
                              <Lightbulb className="h-3.5 w-3.5" aria-hidden />
                            </span>
                            <p className="text-sm text-slate-300">{r}</p>
                          </li>
                        ))}
                      </ol>
                    )}
                    <div className="mt-5 flex items-center gap-1.5 rounded-lg border border-white/[0.06] bg-white/[0.04] px-3 py-2.5 text-xs text-slate-400">
                      <ArrowRight className="h-3.5 w-3.5 text-ai-violet" aria-hidden />
                      Improving these signals raises how favorably AI engines
                      summarize you.
                    </div>
                  </CardContent>
                </Card>
              </FadeIn>
            </div>
          </div>
        )}
      </PlanGate>
    </div>
  );
}

function Skeletons() {
  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center gap-10">
          <Skeleton className="h-[180px] w-[180px] rounded-full" />
          <div className="flex-1 space-y-3">
            <Skeleton className="h-3 w-32" />
            <Skeleton className="h-7 w-3/4" />
            <Skeleton className="h-3 w-40" />
          </div>
        </div>
      </Card>
      <div className="grid gap-6 lg:grid-cols-2">
        {[0, 1].map((c) => (
          <Card key={c} className="p-5">
            <Skeleton className="h-4 w-48" />
            <div className="mt-4 space-y-2.5">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full rounded-lg" />
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
