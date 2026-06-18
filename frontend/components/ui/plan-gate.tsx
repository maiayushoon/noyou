"use client";

import Link from "next/link";
import { Sparkles, Lock, ArrowRight } from "lucide-react";
import { PlanError } from "@/lib/api";
import { Card } from "./card";
import { Button } from "./button";
import { humanize } from "@/lib/utils";

export interface PlanGateProps {
  /** An error from SWR / a request. If it is a PlanError (402), the upsell renders. */
  error: unknown;
  /** What the user was trying to use, for copy. */
  feature?: string;
  children: React.ReactNode;
}

export function isPlanError(error: unknown): error is PlanError {
  return error instanceof PlanError;
}

/**
 * Wrap feature content. If `error` is a 402 PlanError, render an upgrade upsell
 * instead of the children; otherwise render children normally.
 */
export function PlanGate({ error, feature, children }: PlanGateProps) {
  if (!isPlanError(error)) return <>{children}</>;
  const name = feature ?? error.feature;
  return <PlanUpsell feature={name} message={error.message} />;
}

export function PlanUpsell({
  feature,
  message,
}: {
  feature?: string;
  message?: string;
}) {
  return (
    <Card className="overflow-hidden">
      <div className="bg-ai-gradient-soft px-6 pb-6 pt-8">
        <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-ai-gradient text-white shadow-ai">
          <Sparkles className="h-5 w-5" aria-hidden />
        </span>
        <h3 className="mt-4 text-lg font-semibold text-slate-900">
          {feature ? `${humanize(feature)} is a Pro feature` : "Upgrade to unlock"}
        </h3>
        <p className="mt-1.5 max-w-md text-sm text-slate-600">
          {message ||
            "This capability is available on the Pro plan. Upgrade to access AI-powered insights and advanced protection."}
        </p>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <Link href="/accounts">
            <Button variant="ai" leftIcon={<Sparkles className="h-4 w-4" />}>
              Upgrade plan
            </Button>
          </Link>
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500">
            <Lock className="h-3.5 w-3.5" aria-hidden />
            Included in Pro and Business
          </span>
        </div>
      </div>
      <ul className="divide-y divide-[rgba(15,23,42,0.06)] px-6 py-1 text-sm text-slate-600">
        {[
          "AI sentiment & risk analysis on every mention",
          "Pre-Post Check before you publish",
          "AI Visibility scoring across engines",
        ].map((line) => (
          <li key={line} className="flex items-center gap-2 py-2.5">
            <ArrowRight className="h-3.5 w-3.5 text-ai-violet" aria-hidden />
            {line}
          </li>
        ))}
      </ul>
    </Card>
  );
}
