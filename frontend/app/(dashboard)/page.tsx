"use client";

import Link from "next/link";
import useSWR from "swr";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  Bell,
  Brush,
  ExternalLink,
  MessageSquareText,
  Minus,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { api, type DashboardSummary, type ScoreTrendPoint } from "@/lib/api";
import {
  bandColor,
  cn,
  humanize,
  severityColor,
  timeAgo,
} from "@/lib/utils";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  EmptyState,
  RiskBadge,
  SentimentBadge,
  Skeleton,
  Stat,
} from "@/components/ui";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { AuditChecklist } from "@/components/dashboard/audit-checklist";
import { HeroOrb } from "@/components/dashboard/hero-orb";
import { ConnectedAccounts } from "@/components/dashboard/connected-accounts";

export default function OverviewPage() {
  const { data, error, isLoading } = useSWR<DashboardSummary>(
    "dashboard",
    () => api.dashboard()
  );

  return (
    <div className="space-y-6">
      {/* Hero: score ring + band + stat cards */}
      <FadeIn>
        <Card className="relative overflow-hidden">
          {/* Decorative ai-gradient orbs for depth (purely background) */}
          <div
            aria-hidden
            className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-ai-gradient opacity-[0.07] blur-3xl"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -bottom-24 left-1/3 h-48 w-48 rounded-full bg-ai-cyan/10 blur-3xl"
          />
          <div className="relative grid gap-6 p-6 md:grid-cols-[auto,1fr] md:items-center md:gap-10">
            <div className="flex justify-center md:justify-start">
              {isLoading || !data ? (
                <Skeleton className="h-[180px] w-[180px] rounded-full" />
              ) : (
                <HeroOrb
                  score={data.reputation_score}
                  label={bandColor(data.band).label}
                />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-ai-violet" aria-hidden />
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Reputation score
                </span>
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-2">
                <h2 className="text-2xl font-semibold tracking-tight text-slate-900">
                  {isLoading || !data ? (
                    <Skeleton className="h-8 w-64" />
                  ) : (
                    <>Your reputation is {bandColor(data.band).label.toLowerCase()}.</>
                  )}
                </h2>
                {isLoading || !data ? null : (
                  <ScoreDeltaPill
                    delta={data.score_delta}
                    previousScore={data.previous_score}
                  />
                )}
                {!isLoading && data ? (
                  <ScoreSparkline trend={data.score_trend} />
                ) : null}
              </div>
              <p className="mt-1.5 max-w-lg text-sm text-slate-500">
                A <strong className="font-semibold text-slate-600">0–100</strong>{" "}
                measure of how the web and AI engines portray you —{" "}
                <span className="font-medium text-slate-600">higher is safer</span>.
                It blends the sentiment, risk, and recency of every mention we find,
                and updates with each scan.
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-400">
                <span>
                  Last scan {isLoading || !data ? "…" : timeAgo(data.last_scan_at)}
                </span>
                <span className="hidden h-3 w-px bg-hairline sm:inline-block" aria-hidden />
                <span className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <ScaleDot className="bg-emerald-500" label="85–100 Excellent" />
                  <ScaleDot className="bg-emerald-400" label="70–84 Strong" />
                  <ScaleDot className="bg-amber-500" label="50–69 Fair" />
                  <ScaleDot className="bg-orange-500" label="30–49 At risk" />
                  <ScaleDot className="bg-red-500" label="0–29 Critical" />
                </span>
              </div>
              {/* Connected accounts: real people protect their reputation with NoYou */}
              <div className="mt-5 border-t border-hairline pt-4">
                <ConnectedAccounts />
              </div>
            </div>
          </div>
        </Card>
      </FadeIn>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat
          index={0}
          loading={isLoading || !data}
          label="Total mentions"
          value={data?.total_mentions ?? 0}
          hint="Across all sources"
          icon={<MessageSquareText className="h-4.5 w-4.5" />}
          accentClassName="bg-indigo-50 text-ai-indigo"
        />
        <Stat
          index={1}
          loading={isLoading || !data}
          label="High-risk"
          value={data?.high_risk_count ?? 0}
          hint="Need attention"
          icon={<ShieldAlert className="h-4.5 w-4.5" />}
          accentClassName="bg-red-50 text-red-600"
        />
        <Stat
          index={2}
          loading={isLoading || !data}
          label="Unread alerts"
          value={data?.unread_alerts ?? 0}
          hint="New since last visit"
          icon={<Bell className="h-4.5 w-4.5" />}
          accentClassName="bg-amber-50 text-amber-600"
        />
        <Stat
          index={3}
          loading={isLoading || !data}
          label="Cleanup to-do"
          value={data?.active_cleanup_actions ?? 0}
          hint="Suggested actions"
          icon={<Brush className="h-4.5 w-4.5" />}
          accentClassName="bg-violet-50 text-ai-violet"
        />
      </div>

      {/* Gamified profile-audit checklist */}
      <FadeIn delay={0.05}>
        <AuditChecklist dashboard={data} dashboardLoading={isLoading} />
      </FadeIn>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Sentiment mix */}
        <FadeIn delay={0.05} className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Sentiment mix</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading || !data ? (
                <Skeleton className="h-4 w-full rounded-full" />
              ) : (
                <SentimentMix counts={data.sentiment_counts} />
              )}
            </CardContent>
          </Card>
        </FadeIn>

        {/* Recent alerts */}
        <FadeIn delay={0.1} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Recent alerts</CardTitle>
              <Link
                href="/alerts"
                className="inline-flex items-center gap-1 text-xs font-medium text-ai-indigo hover:underline"
              >
                View all
                <ArrowRight className="h-3.5 w-3.5" aria-hidden />
              </Link>
            </CardHeader>
            <CardContent className="pt-0">
              {isLoading || !data ? (
                <RowsSkeleton />
              ) : data.top_alerts.length === 0 ? (
                <EmptyState
                  icon={<Bell className="h-5 w-5" />}
                  title="No alerts right now"
                  description="You're all caught up. New issues will appear here."
                />
              ) : (
                <StaggerList className="divide-y divide-[rgba(15,23,42,0.06)]">
                  {data.top_alerts.slice(0, 5).map((alert) => {
                    const c = severityColor(alert.severity);
                    return (
                      <FadeInItem key={String(alert.id)}>
                        <div className="flex items-start gap-3 py-3">
                          <span
                            className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", c.dot)}
                            aria-hidden
                          />
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-medium text-slate-900">
                              {alert.title}
                            </p>
                            <p className="line-clamp-2 text-sm text-slate-500">
                              {alert.message}
                            </p>
                          </div>
                          <span className="shrink-0 text-xs text-slate-400">
                            {timeAgo(alert.created_at)}
                          </span>
                        </div>
                      </FadeInItem>
                    );
                  })}
                </StaggerList>
              )}
            </CardContent>
          </Card>
        </FadeIn>
      </div>

      {/* Recent high-risk mentions */}
      <FadeIn delay={0.15}>
        <Card>
          <CardHeader>
            <CardTitle>Recent high-risk mentions</CardTitle>
            <Link
              href="/mentions"
              className="inline-flex items-center gap-1 text-xs font-medium text-ai-indigo hover:underline"
            >
              View all mentions
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </Link>
          </CardHeader>
          <CardContent className="pt-0">
            {isLoading || !data ? (
              <RowsSkeleton />
            ) : data.recent_high_risk.length === 0 ? (
              <EmptyState
                icon={<AlertTriangle className="h-5 w-5" />}
                title="No high-risk mentions"
                description="Nothing risky surfaced in the latest scan."
              />
            ) : (
              <StaggerList className="divide-y divide-[rgba(15,23,42,0.06)]">
                {data.recent_high_risk.slice(0, 5).map((m) => (
                  <FadeInItem key={String(m.id)}>
                    <div className="flex items-start gap-3 py-3.5">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                            {humanize(m.source)}
                          </span>
                          {m.url ? (
                            <a
                              href={m.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-slate-400 hover:text-ai-indigo"
                              aria-label="Open source"
                            >
                              <ExternalLink className="h-3.5 w-3.5" aria-hidden />
                            </a>
                          ) : null}
                        </div>
                        <p className="mt-0.5 truncate text-sm font-medium text-slate-900">
                          {m.title || m.content.slice(0, 90)}
                        </p>
                        <p className="mt-0.5 line-clamp-1 text-sm text-slate-500">
                          {m.analysis?.summary || m.content}
                        </p>
                      </div>
                      <div className="flex shrink-0 flex-col items-end gap-1.5">
                        {m.analysis ? (
                          <>
                            <RiskBadge level={m.analysis.risk_level} />
                            <SentimentBadge sentiment={m.analysis.sentiment} />
                          </>
                        ) : (
                          <span className="text-xs text-slate-400">Pending</span>
                        )}
                      </div>
                    </div>
                  </FadeInItem>
                ))}
              </StaggerList>
            )}
          </CardContent>
        </Card>
      </FadeIn>

      {error && !data ? (
        <p className="text-center text-sm text-slate-400">
          Could not load the dashboard. Try running a scan or refreshing.
        </p>
      ) : null}
    </div>
  );
}

function SentimentMix({
  counts,
}: {
  counts: { positive: number; neutral: number; negative: number };
}) {
  const total = counts.positive + counts.neutral + counts.negative || 1;
  const segments = [
    { key: "positive", value: counts.positive, color: "#10b981", label: "Positive" },
    { key: "neutral", value: counts.neutral, color: "#94a3b8", label: "Neutral" },
    { key: "negative", value: counts.negative, color: "#ef4444", label: "Negative" },
  ];
  return (
    <div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-100">
        {segments.map((s) =>
          s.value > 0 ? (
            <div
              key={s.key}
              style={{ width: `${(s.value / total) * 100}%`, backgroundColor: s.color }}
              className="h-full transition-all duration-500"
            />
          ) : null
        )}
      </div>
      <ul className="mt-4 space-y-2.5">
        {segments.map((s) => (
          <li key={s.key} className="flex items-center justify-between text-sm">
            <span className="inline-flex items-center gap-2 text-slate-600">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: s.color }}
                aria-hidden
              />
              {s.label}
            </span>
            <span className="font-medium tabular-nums text-slate-900">
              {s.value}
              <span className="ml-1.5 text-xs text-slate-400">
                {Math.round((s.value / total) * 100)}%
              </span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ScaleDot({ className, label }: { className: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={cn("h-2 w-2 rounded-full", className)} aria-hidden />
      {label}
    </span>
  );
}

/**
 * Change in reputation score since the previous scan. Emerald for a rise,
 * red for a drop, slate for no change. Rounds to one decimal and shows a sign.
 */
function ScoreDeltaPill({
  delta,
  previousScore,
}: {
  delta: number;
  previousScore: number | null;
}) {
  const rounded = Math.round(delta * 10) / 10;
  const isUp = rounded > 0;
  const isDown = rounded < 0;

  const tone = isUp
    ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
    : isDown
      ? "bg-red-50 text-red-700 ring-red-200"
      : "bg-slate-100 text-slate-500 ring-slate-200";

  const Icon = isUp ? ArrowUp : isDown ? ArrowDown : Minus;
  // Avoid "-0"; build an explicit sign + absolute magnitude.
  const sign = isUp ? "+" : isDown ? "-" : "";
  const magnitude = Math.abs(rounded);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset",
        tone
      )}
      title={
        previousScore !== null
          ? `Previous scan: ${Math.round(previousScore)}`
          : "No previous scan to compare"
      }
    >
      <Icon className="h-3.5 w-3.5" aria-hidden />
      <span className="tabular-nums">
        {rounded === 0 ? "No change" : `${sign}${magnitude}`}
      </span>
      <span className="font-normal opacity-70">this scan</span>
    </span>
  );
}

/**
 * Compact, axis-less area sparkline of recent scan scores. Hidden gracefully
 * when there are fewer than 2 points to plot.
 */
function ScoreSparkline({ trend }: { trend: ScoreTrendPoint[] }) {
  if (!trend || trend.length < 2) return null;

  const first = trend[0];
  const last = trend[trend.length - 1];
  if (!first || !last) return null;
  const stroke = last.score >= first.score ? "#10b981" : "#ef4444";

  return (
    <div className="h-9 w-[120px]" aria-hidden>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={trend} margin={{ top: 4, right: 2, bottom: 2, left: 2 }}>
          <defs>
            <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={stroke} stopOpacity={0.28} />
              <stop offset="100%" stopColor={stroke} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="score"
            stroke={stroke}
            strokeWidth={2}
            fill="url(#sparkFill)"
            isAnimationActive={false}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function RowsSkeleton() {
  return (
    <div className="space-y-3 pt-1">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-2 w-2 rounded-full" />
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-3.5 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-3 w-12" />
        </div>
      ))}
    </div>
  );
}
