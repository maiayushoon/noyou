"use client";

import { useState } from "react";
import useSWR from "swr";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { TrendingUp } from "lucide-react";
import { api, type Report } from "@/lib/api";
import { cn, formatDate, humanize } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  EmptyState,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn } from "@/components/motion/fade-in";

const SENTIMENT_COLORS: Record<string, string> = {
  positive: "#10b981",
  neutral: "#94a3b8",
  negative: "#ef4444",
};

const RANGE_OPTIONS: { days: number; label: string }[] = [
  { days: 90, label: "90 Days" },
  { days: 365, label: "1 Year" },
  { days: 1825, label: "5 Years" },
];

export default function TrendsPage() {
  const [days, setDays] = useState(90);
  const { data, error, isLoading } = useSWR<Report>(`reports:${days}`, () =>
    api.reports({ days })
  );

  if (isLoading || !data) {
    return (
      <div>
        <PageHeader
          title="Trends"
          description="Score history, sentiment over time, and risk by category."
          actions={<RangePills days={days} onChange={setDays} />}
        />
        {error ? (
          <Card>
            <EmptyState
              icon={<TrendingUp className="h-5 w-5" />}
              title="Could not load trends"
              description="The API may be unreachable. Try running a scan or refreshing."
            />
          </Card>
        ) : (
          <ChartsSkeleton />
        )}
      </div>
    );
  }

  const scoreSeries = data.score_history.map((p) => ({
    date: formatDate(p.date),
    score: p.score,
  }));
  const mentionsSeries = data.mentions_over_time.map((p) => ({
    date: formatDate(p.date),
    count: p.count,
  }));
  const sentimentData = [
    { name: "Positive", key: "positive", value: data.sentiment_distribution.positive },
    { name: "Neutral", key: "neutral", value: data.sentiment_distribution.neutral },
    { name: "Negative", key: "negative", value: data.sentiment_distribution.negative },
  ];
  const sourceData = Object.entries(data.mentions_by_source)
    .map(([name, value]) => ({ name: humanize(name), value }))
    .sort((a, b) => b.value - a.value);
  const riskData = Object.entries(data.risk_by_category)
    .map(([name, value]) => ({ name: humanize(name), value }))
    .sort((a, b) => b.value - a.value);

  return (
    <div>
      <PageHeader
        title="Trends"
        description="Score history, sentiment over time, and risk broken down by category."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <RangePills days={days} onChange={setDays} />
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/[0.06] px-3 py-1 text-xs font-semibold text-slate-300">
              <TrendingUp className="h-3.5 w-3.5" aria-hidden />
              Score {data.reputation_score}
            </span>
          </div>
        }
      />

      <div className="space-y-6">
        <FadeIn>
          <Card>
            <CardHeader>
              <CardTitle>Reputation score over time</CardTitle>
            </CardHeader>
            <CardContent>
              {scoreSeries.length === 0 ? (
                <NoData />
              ) : (
                <ResponsiveContainer width="100%" height={260}>
                  <AreaChart data={scoreSeries} margin={{ left: -18, right: 8, top: 8 }}>
                    <defs>
                      <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: "#94a3b8" }}
                      tickLine={false}
                      axisLine={false}
                      minTickGap={24}
                    />
                    <YAxis
                      domain={[0, 100]}
                      tick={{ fontSize: 11, fill: "#94a3b8" }}
                      tickLine={false}
                      axisLine={false}
                      width={42}
                    />
                    <Tooltip content={<ChartTooltip suffix="" />} />
                    <Area
                      type="monotone"
                      dataKey="score"
                      stroke="#6366f1"
                      strokeWidth={2.5}
                      fill="url(#scoreFill)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </FadeIn>

        <div className="grid gap-6 lg:grid-cols-2">
          <FadeIn delay={0.05}>
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Mentions over time</CardTitle>
              </CardHeader>
              <CardContent>
                {mentionsSeries.length === 0 ? (
                  <NoData />
                ) : (
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={mentionsSeries} margin={{ left: -18, right: 8, top: 8 }}>
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11, fill: "#94a3b8" }}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={24}
                      />
                      <YAxis
                        allowDecimals={false}
                        tick={{ fontSize: 11, fill: "#94a3b8" }}
                        tickLine={false}
                        axisLine={false}
                        width={32}
                      />
                      <Tooltip content={<ChartTooltip suffix=" mentions" />} cursor={{ fill: "rgba(99,102,241,0.06)" }} />
                      <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} maxBarSize={40} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn delay={0.1}>
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Sentiment distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={sentimentData} margin={{ left: -18, right: 8, top: 8 }}>
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 11, fill: "#94a3b8" }}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      allowDecimals={false}
                      tick={{ fontSize: 11, fill: "#94a3b8" }}
                      tickLine={false}
                      axisLine={false}
                      width={32}
                    />
                    <Tooltip content={<ChartTooltip suffix="" />} cursor={{ fill: "rgba(99,102,241,0.06)" }} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={56}>
                      {sentimentData.map((d) => (
                        <Cell key={d.key} fill={SENTIMENT_COLORS[d.key]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </FadeIn>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <FadeIn delay={0.05}>
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Mentions by source</CardTitle>
              </CardHeader>
              <CardContent>
                <DistributionList data={sourceData} color="#6366f1" emptyLabel="No mentions yet" />
              </CardContent>
            </Card>
          </FadeIn>
          <FadeIn delay={0.1}>
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Risk by category</CardTitle>
              </CardHeader>
              <CardContent>
                <DistributionList data={riskData} color="#ef4444" emptyLabel="No risks flagged" />
              </CardContent>
            </Card>
          </FadeIn>
        </div>
      </div>
    </div>
  );
}

function RangePills({
  days,
  onChange,
}: {
  days: number;
  onChange: (days: number) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {RANGE_OPTIONS.map((r) => (
        <button
          key={r.days}
          type="button"
          onClick={() => onChange(r.days)}
          className={cn(
            "rounded-full px-3 py-1.5 text-xs font-medium transition-colors",
            days === r.days
              ? "bg-ai-gradient text-white shadow-ai"
              : "bg-white/[0.04] text-slate-300 ring-1 ring-inset ring-white/[0.10] hover:bg-white/[0.06] hover:text-slate-100"
          )}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}

function DistributionList({
  data,
  color,
  emptyLabel,
}: {
  data: { name: string; value: number }[];
  color: string;
  emptyLabel: string;
}) {
  if (data.length === 0) {
    return <p className="py-6 text-center text-sm text-slate-400">{emptyLabel}</p>;
  }
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <ul className="space-y-3">
      {data.map((d) => (
        <li key={d.name}>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-300">{d.name}</span>
            <span className="font-medium tabular-nums text-slate-100">{d.value}</span>
          </div>
          <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${(d.value / max) * 100}%`, backgroundColor: color }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}

function ChartTooltip({
  active,
  payload,
  label,
  suffix,
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
  suffix: string;
}) {
  const first = payload?.[0];
  if (!active || !first) return null;
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b0b12]/95 px-3 py-2 shadow-[0_8px_30px_-8px_rgba(0,0,0,0.6)] backdrop-blur-sm">
      <p className="text-xs font-medium text-slate-400">{label}</p>
      <p className="text-sm font-semibold text-slate-100">
        {first.value}
        {suffix}
      </p>
    </div>
  );
}

function NoData() {
  return <p className="py-12 text-center text-sm text-slate-400">Run a scan to start building history.</p>;
}

function ChartsSkeleton() {
  return (
    <div className="space-y-6">
      <Card className="p-5">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="mt-4 h-[240px] w-full rounded-lg" />
      </Card>
      <div className="grid gap-6 lg:grid-cols-2">
        {[0, 1].map((i) => (
          <Card key={i} className="p-5">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="mt-4 h-[200px] w-full rounded-lg" />
          </Card>
        ))}
      </div>
    </div>
  );
}
