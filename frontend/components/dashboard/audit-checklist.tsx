"use client";

import Link from "next/link";
import useSWR from "swr";
import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowRight,
  Check,
  CircleDashed,
  ListChecks,
  PartyPopper,
} from "lucide-react";
import { api, type DashboardSummary } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button, Card, CardContent, CardHeader, CardTitle, Skeleton } from "@/components/ui";

/* -------------------------------------------------------------------------- */
/*  Gamified profile-audit checklist                                          */
/*                                                                            */
/*  Derives 5 actionable steps purely from data already available to the      */
/*  dashboard — no new endpoints. Each incomplete step deep-links to the      */
/*  page where the user can complete it. Renders a Skeleton while loading     */
/*  and never throws if a fetch fails (failed fetches read as "not done").    */
/* -------------------------------------------------------------------------- */

interface AuditStep {
  id: string;
  label: string;
  description: string;
  href: string;
  cta: string;
  done: boolean;
}

export function AuditChecklist({
  dashboard,
  dashboardLoading,
}: {
  dashboard: DashboardSummary | undefined;
  dashboardLoading: boolean;
}) {
  const reduce = useReducedMotion();

  // Independent fetches — failures resolve to undefined and read as "not done".
  const { data: accounts, isLoading: accountsLoading } = useSWR(
    "accounts",
    () => api.listAccounts(),
    { shouldRetryOnError: false }
  );
  const { data: connections, isLoading: connectionsLoading } = useSWR(
    "connections",
    () => api.listConnections(),
    { shouldRetryOnError: false }
  );

  const loading =
    dashboardLoading || !dashboard || accountsLoading || connectionsLoading;

  if (loading) {
    return <ChecklistSkeleton />;
  }

  const hasConnected = (connections ?? []).some(
    (c) => c.status === "connected"
  );

  const steps: AuditStep[] = [
    {
      id: "identity",
      label: "Add an identity to monitor",
      description: "Tell NoYou which handles and names to watch.",
      href: "/accounts",
      cta: "Add identity",
      done: (accounts ?? []).length > 0,
    },
    {
      id: "scan",
      label: "Run your first scan",
      description: "Sweep the web and AI engines for mentions of you.",
      href: "/accounts",
      cta: "Run a scan",
      done: !!dashboard.last_scan_at,
    },
    {
      id: "connect",
      label: "Connect an account",
      description: "Link a platform so NoYou can act on your behalf.",
      href: "/connections",
      cta: "Connect",
      done: hasConnected,
    },
    {
      id: "high-risk",
      label: "Resolve a high-risk mention",
      description: "Clear anything flagged as a reputation risk.",
      href: "/mentions",
      cta: "Review mentions",
      done: dashboard.high_risk_count === 0,
    },
    {
      id: "alerts",
      label: "Clear your alerts",
      description: "Stay on top of new issues as they surface.",
      href: "/alerts",
      cta: "View alerts",
      done: dashboard.unread_alerts === 0,
    },
  ];

  const completed = steps.filter((s) => s.done).length;
  const total = steps.length;
  const allDone = completed === total;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ListChecks className="h-4 w-4 text-ai-violet" aria-hidden />
          Profile audit
        </CardTitle>
        <span className="text-xs font-medium tabular-nums text-slate-400">
          {completed} of {total} done
        </span>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
          <ProgressRing completed={completed} total={total} />
          <p className="text-sm text-slate-500">
            {allDone ? (
              <span className="inline-flex items-center gap-1.5 font-medium text-emerald-600">
                <PartyPopper className="h-4 w-4" aria-hidden />
                You&rsquo;ve completed every step. Nicely done.
              </span>
            ) : (
              <>
                Strengthen your reputation setup. Knock out these steps to get
                the most out of NoYou.
              </>
            )}
          </p>
        </div>

        <ul className="mt-5 space-y-2.5">
          {steps.map((step, i) => (
            <motion.li
              key={step.id}
              initial={reduce ? false : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: i * 0.04, ease: "easeOut" }}
              className={cn(
                "flex items-center gap-3 rounded-xl border px-3.5 py-3 transition-colors",
                step.done
                  ? "border-emerald-100 bg-emerald-50/50"
                  : "border-hairline bg-white"
              )}
            >
              <span
                className={cn(
                  "inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
                  step.done
                    ? "bg-emerald-500 text-white"
                    : "bg-slate-100 text-slate-400"
                )}
                aria-hidden
              >
                {step.done ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <CircleDashed className="h-4 w-4" />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <p
                  className={cn(
                    "truncate text-sm font-medium",
                    step.done ? "text-slate-500 line-through" : "text-slate-900"
                  )}
                >
                  {step.label}
                </p>
                {!step.done ? (
                  <p className="truncate text-xs text-slate-400">
                    {step.description}
                  </p>
                ) : null}
              </div>
              {!step.done ? (
                <Link href={step.href} className="shrink-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    rightIcon={<ArrowRight className="h-3.5 w-3.5" />}
                    className="text-ai-indigo hover:bg-indigo-50"
                  >
                    {step.cta}
                  </Button>
                </Link>
              ) : null}
            </motion.li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

/* ------------------------------- Progress ring ---------------------------- */

function ProgressRing({
  completed,
  total,
  size = 64,
  strokeWidth = 7,
}: {
  completed: number;
  total: number;
  size?: number;
  strokeWidth?: number;
}) {
  const reduce = useReducedMotion();
  const pct = total > 0 ? completed / total : 0;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - pct);

  return (
    <div
      className="relative shrink-0"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`${completed} of ${total} audit steps complete`}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(15,23,42,0.07)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#10b981"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: reduce ? offset : circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={reduce ? { duration: 0 } : { duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-semibold tabular-nums text-slate-900">
          {Math.round(pct * 100)}%
        </span>
      </div>
    </div>
  );
}

/* --------------------------------- Skeleton ------------------------------- */

function ChecklistSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-3 w-16" />
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center gap-5">
          <Skeleton className="h-16 w-16 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3.5 w-3/4" />
            <Skeleton className="h-3.5 w-1/2" />
          </div>
        </div>
        <div className="mt-5 space-y-2.5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-xl border border-hairline px-3.5 py-3"
            >
              <Skeleton className="h-7 w-7 rounded-full" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-3.5 w-2/5" />
                <Skeleton className="h-3 w-3/5" />
              </div>
              <Skeleton className="h-7 w-20 rounded-lg" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
