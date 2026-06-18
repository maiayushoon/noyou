"use client";

import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn } from "@/components/motion/fade-in";

/**
 * Build-clean placeholder for feature pages. The Features phase replaces the
 * page body with real SWR-driven content following the same shell.
 */
export function FeatureStub({
  title,
  description,
  icon: Icon,
  ai = false,
}: {
  title: string;
  description: string;
  icon: LucideIcon;
  ai?: boolean;
}) {
  return (
    <FadeIn>
      <PageHeader
        title={title}
        description={description}
        actions={ai ? <Badge variant="ai" dot dotClassName="bg-white">AI</Badge> : undefined}
      />
      <Card className="flex flex-col items-center justify-center px-6 py-16 text-center">
        <span className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-ai-gradient-soft text-ai-violet">
          <Icon className="h-6 w-6" aria-hidden />
        </span>
        <p className="text-sm font-semibold text-slate-900">Coming together</p>
        <p className="mt-1 max-w-sm text-sm text-slate-500">
          This view is part of the foundation. The feature team wires it to the
          API next, following the shared layout and components.
        </p>
      </Card>
    </FadeIn>
  );
}
