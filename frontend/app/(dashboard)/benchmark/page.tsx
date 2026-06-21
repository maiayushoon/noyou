"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import {
  BarChart3,
  Crown,
  Plus,
  Trash2,
  TrendingUp,
} from "lucide-react";
import {
  api,
  type BenchmarkEntry,
  type BenchmarkReport,
  type Competitor,
  isPlanError,
} from "@/lib/api";
import { bandColor, cn } from "@/lib/utils";
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  EmptyState,
  PlanGate,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { useToast } from "@/lib/toast";

// Brightened band label colors for readable contrast on the dark surface
// (mirrors bandColor() in lib/utils, which targets light backgrounds).
const BAND_TEXT_DARK: Record<string, string> = {
  excellent: "text-emerald-300",
  high: "text-emerald-300",
  medium: "text-amber-300",
  low: "text-orange-300",
  critical: "text-red-300",
};

export default function BenchmarkPage() {
  const toast = useToast();
  const { mutate } = useSWRConfig();
  const [name, setName] = useState("");
  const [adding, setAdding] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);

  const competitors = useSWR<Competitor[]>("competitors", () =>
    api.listCompetitors()
  );
  const report = useSWR<BenchmarkReport>("benchmark", () =>
    api.benchmarkReport()
  );

  function refresh() {
    mutate("competitors");
    mutate("benchmark");
  }

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setAdding(true);
    try {
      await api.addCompetitor({ name: name.trim() });
      setName("");
      refresh();
      toast.success("Competitor added", "We'll benchmark them in your next scan.");
    } catch (err) {
      if (isPlanError(err)) {
        toast.error("Benchmarking is a Pro feature", "Upgrade to compare against competitors.");
      } else {
        toast.error("Could not add competitor", err instanceof Error ? err.message : undefined);
      }
    } finally {
      setAdding(false);
    }
  }

  async function remove(c: Competitor) {
    setBusyId(String(c.id));
    try {
      await api.removeCompetitor(c.id);
      refresh();
      toast.success("Competitor removed");
    } catch (err) {
      toast.error("Could not remove competitor", err instanceof Error ? err.message : undefined);
    } finally {
      setBusyId(null);
    }
  }

  // Either query 402-ing means the feature is gated.
  const gateError = isPlanError(report.error)
    ? report.error
    : isPlanError(competitors.error)
    ? competitors.error
    : null;

  const entries = [...(report.data?.entries ?? [])].sort(
    (a, b) => b.reputation_score - a.reputation_score
  );

  return (
    <div>
      <PageHeader
        title="Benchmark"
        description="See how your reputation stacks up against competitors across score, volume, and sentiment."
        actions={
          <Badge variant="ai" dot dotClassName="bg-white">
            Pro
          </Badge>
        }
      />

      <PlanGate error={gateError} feature="benchmarking">
        <div className="grid gap-6 lg:grid-cols-[1fr,1.5fr]">
          {/* Competitors management */}
          <FadeIn>
            <Card>
              <CardHeader>
                <CardTitle>Competitors</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={add} className="flex gap-2">
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Brand or person to track"
                    className="min-w-0 flex-1 rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
                  />
                  <Button
                    type="submit"
                    variant="ai"
                    loading={adding}
                    disabled={!name.trim()}
                    leftIcon={!adding ? <Plus className="h-4 w-4" /> : undefined}
                  >
                    Add
                  </Button>
                </form>

                <div className="mt-4">
                  {competitors.isLoading ? (
                    <div className="space-y-2">
                      {Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-11 w-full rounded-lg" />
                      ))}
                    </div>
                  ) : (competitors.data?.length ?? 0) === 0 ? (
                    <p className="py-6 text-center text-sm text-slate-400">
                      No competitors yet. Add a few to start comparing.
                    </p>
                  ) : (
                    <StaggerList className="space-y-2">
                      {competitors.data!.map((c) => (
                        <FadeInItem key={String(c.id)}>
                          <div className="flex items-center gap-3 rounded-lg border border-white/[0.08] bg-white/[0.03] p-3 transition-colors hover:border-white/[0.12]">
                            <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/[0.06] text-slate-400">
                              <TrendingUp className="h-4 w-4" aria-hidden />
                            </span>
                            <p className="min-w-0 flex-1 truncate text-sm font-medium text-slate-100">
                              {c.name}
                            </p>
                            <Button
                              size="icon"
                              variant="ghost"
                              loading={busyId === String(c.id)}
                              onClick={() => remove(c)}
                              aria-label="Remove competitor"
                            >
                              <Trash2 className="h-4 w-4 text-slate-400" />
                            </Button>
                          </div>
                        </FadeInItem>
                      ))}
                    </StaggerList>
                  )}
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          {/* Leaderboard */}
          <FadeIn delay={0.05}>
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Reputation leaderboard</CardTitle>
                {report.data ? (
                  <span className="text-xs text-slate-400">
                    {entries.length} compared
                  </span>
                ) : null}
              </CardHeader>
              <CardContent className="pt-0">
                {report.isLoading ? (
                  <div className="space-y-2.5 pt-2">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <Skeleton key={i} className="h-20 w-full rounded-lg" />
                    ))}
                  </div>
                ) : report.error && !gateError ? (
                  <EmptyState
                    icon={<BarChart3 className="h-5 w-5" />}
                    title="Could not load benchmark"
                    description="The API may be unreachable. Try refreshing."
                  />
                ) : entries.length === 0 ? (
                  <EmptyState
                    icon={<BarChart3 className="h-5 w-5" />}
                    title="Nothing to compare yet"
                    description="Add competitors and run a scan to build the leaderboard."
                  />
                ) : (
                  <StaggerList className="space-y-2.5">
                    {entries.map((e, i) => (
                      <FadeInItem key={e.name}>
                        <LeaderRow entry={e} rank={i + 1} />
                      </FadeInItem>
                    ))}
                  </StaggerList>
                )}
              </CardContent>
            </Card>
          </FadeIn>
        </div>
      </PlanGate>
    </div>
  );
}

function LeaderRow({ entry, rank }: { entry: BenchmarkEntry; rank: number }) {
  const band = bandColor(entry.band);
  const total =
    entry.sentiment.positive + entry.sentiment.neutral + entry.sentiment.negative || 1;
  const segments = [
    { v: entry.sentiment.positive, c: "#10b981" },
    { v: entry.sentiment.neutral, c: "#94a3b8" },
    { v: entry.sentiment.negative, c: "#ef4444" },
  ];

  return (
    <div
      className={cn(
        "rounded-xl border p-4 transition-colors",
        entry.is_you
          ? "border-ai-indigo/40 bg-ai-gradient-soft shadow-[0_0_40px_-12px_rgba(216,184,106,0.45)]"
          : "border-white/[0.08] bg-white/[0.03] hover:border-white/[0.12]"
      )}
    >
      <div className="flex items-center gap-3">
        <span
          className={cn(
            "inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold",
            rank === 1
              ? "bg-amber-500/15 text-amber-300"
              : "bg-white/[0.06] text-slate-400"
          )}
        >
          {rank}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="truncate text-sm font-semibold text-slate-100">{entry.name}</p>
            {entry.is_you ? (
              <Badge variant="ai" className="gap-1">
                <Crown className="h-3 w-3" aria-hidden /> You
              </Badge>
            ) : null}
          </div>
          <p className="text-xs text-slate-400">{entry.total_mentions} mentions tracked</p>
        </div>
        <div className="shrink-0 text-right">
          <p className="text-xl font-semibold tabular-nums text-slate-100">
            {Math.round(entry.reputation_score)}
          </p>
          <span className={cn("text-xs font-medium", BAND_TEXT_DARK[entry.band] ?? "text-slate-300")}>
            {band.label}
          </span>
        </div>
      </div>
      <div className="mt-3 flex h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
        {segments.map((s, i) =>
          s.v > 0 ? (
            <div
              key={i}
              style={{ width: `${(s.v / total) * 100}%`, backgroundColor: s.c }}
              className="h-full"
            />
          ) : null
        )}
      </div>
    </div>
  );
}
