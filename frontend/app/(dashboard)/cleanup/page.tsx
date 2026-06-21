"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import {
  Brush,
  CheckCircle2,
  Eye,
  PlayCircle,
  Sparkles,
  Wand2,
  X,
} from "lucide-react";
import {
  api,
  type CleanupAction,
  type CleanupAutoSummary,
  type CleanupStatus,
  isPlanError,
} from "@/lib/api";
import { cn, humanize, timeAgo } from "@/lib/utils";
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  EmptyState,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { useToast } from "@/lib/toast";

const STATUS_TABS: { key: CleanupStatus | "all"; label: string }[] = [
  { key: "suggested", label: "Suggested" },
  { key: "in_progress", label: "In progress" },
  { key: "completed", label: "Completed" },
  { key: "dismissed", label: "Dismissed" },
  { key: "all", label: "All" },
];

export default function CleanupPage() {
  const toast = useToast();
  const { mutate } = useSWRConfig();
  const [status, setStatus] = useState<CleanupStatus | "all">("suggested");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [autoBusy, setAutoBusy] = useState<"run" | "preview" | null>(null);
  const [preview, setPreview] = useState<CleanupAutoSummary | null>(null);

  const key = `cleanup:${status}`;
  const { data, error, isLoading } = useSWR<CleanupAction[]>(key, () =>
    api.listCleanup({ status: status === "all" ? undefined : status, limit: 100 })
  );

  const actions = data ?? [];

  function refresh() {
    mutate((k) => typeof k === "string" && k.startsWith("cleanup"));
    mutate("dashboard");
  }

  async function update(a: CleanupAction, next: CleanupStatus) {
    setBusyId(String(a.id));
    try {
      await api.updateCleanup(a.id, next);
      refresh();
      toast.success("Action updated", `Marked as ${humanize(next)}.`);
    } catch (err) {
      toast.error("Could not update action", err instanceof Error ? err.message : undefined);
    } finally {
      setBusyId(null);
    }
  }

  async function runAuto(dryRun: boolean) {
    setAutoBusy(dryRun ? "preview" : "run");
    try {
      const summary = await api.autoExecuteCleanup(dryRun);
      if (dryRun) {
        setPreview(summary);
        toast.info(
          "Preview ready",
          `${summary.executed} would run automatically, ${summary.drafted} drafted.`
        );
      } else {
        setPreview(null);
        refresh();
        toast.success(
          "Automated cleanup complete",
          `${summary.executed} applied · ${summary.drafted} drafted · ${summary.skipped} skipped.`
        );
      }
    } catch (err) {
      if (isPlanError(err)) {
        toast.error(
          "Automated cleanup is a Pro feature",
          "Upgrade to let NoYou apply safe actions for you."
        );
      } else {
        toast.error("Could not run automated cleanup", err instanceof Error ? err.message : undefined);
      }
    } finally {
      setAutoBusy(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Cleanup"
        description="Guided actions to remove, archive, or push down harmful content — done for you where it's safe."
      />

      {/* Automation banner */}
      <FadeIn>
        <Card className="mb-5 overflow-hidden">
          <div className="flex flex-col gap-4 bg-ai-gradient-soft p-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-ai-gradient text-white shadow-ai">
                <Wand2 className="h-5 w-5" aria-hidden />
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold text-slate-100">Automated cleanup</p>
                  <Badge variant="ai" dot dotClassName="bg-white">
                    Pro
                  </Badge>
                </div>
                <p className="mt-0.5 max-w-md text-sm text-slate-300">
                  NoYou applies safe actions (archive, monitor) automatically and
                  drafts the riskier ones for your review.
                </p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Button
                variant="outline"
                onClick={() => runAuto(true)}
                loading={autoBusy === "preview"}
                disabled={autoBusy !== null}
                leftIcon={<Eye className="h-4 w-4" />}
              >
                Preview
              </Button>
              <Button
                variant="ai"
                onClick={() => runAuto(false)}
                loading={autoBusy === "run"}
                disabled={autoBusy !== null}
                leftIcon={<Sparkles className="h-4 w-4" />}
              >
                Auto-run safe actions
              </Button>
            </div>
          </div>

          {preview ? (
            <div className="border-t border-white/[0.08] px-5 py-4">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
                Dry-run preview — nothing was changed
              </p>
              <div className="mb-3 flex flex-wrap gap-2 text-xs">
                <PreviewStat label="Would auto-run" value={preview.executed} tone="emerald" />
                <PreviewStat label="Would draft" value={preview.drafted} tone="amber" />
                <PreviewStat label="Skipped" value={preview.skipped} tone="slate" />
              </div>
              <ul className="space-y-1.5">
                {preview.details.slice(0, 6).map((d, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                    <span
                      className={cn(
                        "h-1.5 w-1.5 rounded-full",
                        d.outcome === "executed"
                          ? "bg-emerald-400"
                          : d.outcome === "drafted"
                          ? "bg-amber-400"
                          : "bg-slate-500"
                      )}
                      aria-hidden
                    />
                    <span className="font-medium text-slate-100">{humanize(d.action_type)}</span>
                    <span className="text-slate-500">·</span>
                    <span className="truncate">{d.note}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </Card>
      </FadeIn>

      {/* Status filter */}
      <FadeIn>
        <div className="mb-5 flex flex-wrap gap-1.5">
          {STATUS_TABS.map((t) => (
            <button
              key={t.key}
              type="button"
              onClick={() => setStatus(t.key)}
              className={cn(
                "rounded-full px-3 py-1.5 text-xs font-medium transition-colors",
                status === t.key
                  ? "bg-ai-gradient text-white shadow-ai"
                  : "bg-white/[0.03] text-slate-300 ring-1 ring-inset ring-white/[0.10] hover:bg-white/[0.06] hover:text-slate-100"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </FadeIn>

      {isLoading ? (
        <ListSkeleton />
      ) : error ? (
        <Card>
          <EmptyState
            icon={<Brush className="h-5 w-5" />}
            title="Could not load cleanup actions"
            description="The API may be unreachable. Try refreshing in a moment."
          />
        </Card>
      ) : actions.length === 0 ? (
        <Card>
          <EmptyState
            icon={<CheckCircle2 className="h-5 w-5" />}
            title="Nothing to clean up here"
            description="No actions in this state. Run a scan to surface new suggestions."
          />
        </Card>
      ) : (
        <StaggerList className="space-y-3">
          {actions.map((a) => (
            <FadeInItem key={String(a.id)}>
              <ActionRow
                action={a}
                busy={busyId === String(a.id)}
                onUpdate={update}
              />
            </FadeInItem>
          ))}
        </StaggerList>
      )}
    </div>
  );
}

function ActionRow({
  action: a,
  busy,
  onUpdate,
}: {
  action: CleanupAction;
  busy: boolean;
  onUpdate: (a: CleanupAction, next: CleanupStatus) => void;
}) {
  return (
    <Card interactive className="p-4 sm:p-5">
      <CardHeader className="p-0 pb-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <CardTitle>{a.title}</CardTitle>
            <span className="rounded-full bg-white/[0.06] px-2 py-0.5 text-xs font-medium text-slate-400">
              {humanize(a.action_type)}
            </span>
            {a.automated ? (
              <Badge variant="ai" dot dotClassName="bg-white">
                Auto
              </Badge>
            ) : null}
          </div>
        </div>
        <span className="shrink-0 text-xs text-slate-400">{timeAgo(a.created_at)}</span>
      </CardHeader>
      <CardContent className="p-0">
        <p className="text-sm text-slate-300">{a.instructions}</p>
        <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-white/[0.08] pt-3">
          <StatusTag status={a.status} />
          <div className="ml-auto flex items-center gap-2">
            {a.status === "suggested" ? (
              <Button
                size="sm"
                variant="outline"
                loading={busy}
                onClick={() => onUpdate(a, "in_progress")}
                leftIcon={<PlayCircle className="h-3.5 w-3.5" />}
              >
                Start
              </Button>
            ) : null}
            {a.status !== "completed" ? (
              <Button
                size="sm"
                variant="ai"
                loading={busy}
                onClick={() => onUpdate(a, "completed")}
                leftIcon={<CheckCircle2 className="h-3.5 w-3.5" />}
              >
                Mark done
              </Button>
            ) : null}
            {a.status !== "dismissed" && a.status !== "completed" ? (
              <Button
                size="sm"
                variant="ghost"
                loading={busy}
                onClick={() => onUpdate(a, "dismissed")}
                leftIcon={<X className="h-3.5 w-3.5" />}
              >
                Dismiss
              </Button>
            ) : null}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StatusTag({ status }: { status: CleanupStatus }) {
  const map: Record<CleanupStatus, string> = {
    suggested: "bg-ai-indigo/15 text-amber-200",
    in_progress: "bg-amber-500/15 text-amber-300",
    completed: "bg-emerald-500/15 text-emerald-300",
    dismissed: "bg-white/[0.06] text-slate-400",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        map[status]
      )}
    >
      {humanize(status)}
    </span>
  );
}

function PreviewStat({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "emerald" | "amber" | "slate";
}) {
  const tones = {
    emerald: "bg-emerald-500/15 text-emerald-300",
    amber: "bg-amber-500/15 text-amber-300",
    slate: "bg-white/[0.06] text-slate-300",
  };
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-medium", tones[tone])}>
      <span className="tabular-nums">{value}</span>
      {label}
    </span>
  );
}

function ListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i} className="p-5">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="mt-3 h-3 w-3/4" />
          <Skeleton className="mt-4 h-8 w-40 rounded-lg" />
        </Card>
      ))}
    </div>
  );
}
