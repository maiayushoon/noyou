"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import {
  Archive,
  ExternalLink,
  Filter,
  MessageSquareText,
  PenLine,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  Trash2,
} from "lucide-react";
import {
  api,
  isPlanError,
  type FixSuggestion,
  type Mention,
  type MentionStatus,
  type SentimentLabel,
} from "@/lib/api";
import { cn, humanize, timeAgo } from "@/lib/utils";
import {
  Button,
  Card,
  EmptyState,
  RiskBadge,
  SentimentBadge,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { useToast } from "@/lib/toast";

type StatusFilter = MentionStatus | "all";
type SentimentFilter = SentimentLabel | "all";

const STATUS_TABS: { key: StatusFilter; label: string }[] = [
  { key: "active", label: "Active" },
  { key: "archived", label: "Archived" },
  { key: "removal_requested", label: "Removal requested" },
  { key: "removed", label: "Removed" },
  { key: "all", label: "All" },
];

const SENTIMENT_CHIPS: { key: SentimentFilter; label: string }[] = [
  { key: "all", label: "Any sentiment" },
  { key: "negative", label: "Negative" },
  { key: "neutral", label: "Neutral" },
  { key: "positive", label: "Positive" },
];

const RISK_CHIPS: { key: number; label: string }[] = [
  { key: 0, label: "Any risk" },
  { key: 2, label: "Risk 2+" },
  { key: 3, label: "Risk 3+" },
  { key: 4, label: "High risk" },
];

export default function MentionsPage() {
  const toast = useToast();
  const { mutate } = useSWRConfig();
  const [status, setStatus] = useState<StatusFilter>("active");
  const [sentiment, setSentiment] = useState<SentimentFilter>("all");
  const [minRisk, setMinRisk] = useState(0);
  const [busyId, setBusyId] = useState<string | null>(null);

  const key = `mentions:${status}:${sentiment}:${minRisk}`;
  const { data, error, isLoading } = useSWR<Mention[]>(key, () =>
    api.listMentions({
      status: status === "all" ? undefined : status,
      sentiment: sentiment === "all" ? undefined : sentiment,
      min_risk: minRisk || undefined,
      limit: 100,
    })
  );

  const mentions = data ?? [];
  const negativeCount = mentions.filter(
    (m) => m.analysis?.sentiment === "negative"
  ).length;

  async function setMentionStatus(m: Mention, next: MentionStatus) {
    setBusyId(String(m.id));
    try {
      await api.updateMentionStatus(m.id, next);
      await mutate((k) => typeof k === "string" && k.startsWith("mentions"));
      mutate("dashboard");
      toast.success("Mention updated", `Marked as ${humanize(next)}.`);
    } catch (err) {
      toast.error(
        "Could not update mention",
        err instanceof Error ? err.message : undefined
      );
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Mentions"
        description="Everything the web and AI engines say about you, analyzed and triaged."
        actions={
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400">
            <Filter className="h-3.5 w-3.5" aria-hidden />
            {isLoading ? "…" : `${mentions.length} shown`}
            {negativeCount > 0 ? (
              <span className="ml-1 inline-flex items-center gap-1 rounded-full bg-red-500/15 px-2 py-0.5 text-red-300">
                <ShieldAlert className="h-3 w-3" aria-hidden />
                {negativeCount} negative
              </span>
            ) : null}
          </span>
        }
      />

      <FadeIn>
        <div className="mb-5 space-y-3">
          <div className="flex flex-wrap gap-1.5">
            {STATUS_TABS.map((t) => (
              <FilterPill
                key={t.key}
                active={status === t.key}
                onClick={() => setStatus(t.key)}
              >
                {t.label}
              </FilterPill>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {SENTIMENT_CHIPS.map((c) => (
              <FilterPill
                key={c.key}
                subtle
                active={sentiment === c.key}
                onClick={() => setSentiment(c.key)}
              >
                {c.label}
              </FilterPill>
            ))}
            <span className="mx-1 h-4 w-px bg-white/[0.08]" aria-hidden />
            {RISK_CHIPS.map((c) => (
              <FilterPill
                key={c.key}
                subtle
                active={minRisk === c.key}
                onClick={() => setMinRisk(c.key)}
              >
                {c.label}
              </FilterPill>
            ))}
          </div>
        </div>
      </FadeIn>

      {isLoading ? (
        <ListSkeleton />
      ) : error ? (
        <Card>
          <EmptyState
            icon={<MessageSquareText className="h-5 w-5" />}
            title="Could not load mentions"
            description="The API may be unreachable. Try running a scan or refreshing."
          />
        </Card>
      ) : mentions.length === 0 ? (
        <Card>
          <EmptyState
            icon={<MessageSquareText className="h-5 w-5" />}
            title="No mentions match these filters"
            description="Run a scan from the top bar, or loosen the filters above."
          />
        </Card>
      ) : (
        <StaggerList className="space-y-3">
          {mentions.map((m) => (
            <FadeInItem key={String(m.id)}>
              <MentionRow
                mention={m}
                busy={busyId === String(m.id)}
                onUpdate={setMentionStatus}
              />
            </FadeInItem>
          ))}
        </StaggerList>
      )}
    </div>
  );
}

function MentionRow({
  mention: m,
  busy,
  onUpdate,
}: {
  mention: Mention;
  busy: boolean;
  onUpdate: (m: Mention, next: MentionStatus) => void;
}) {
  const toast = useToast();
  const [suggesting, setSuggesting] = useState(false);
  const [fix, setFix] = useState<FixSuggestion | null>(null);

  async function getSuggestion() {
    setSuggesting(true);
    try {
      const result = await api.suggestFix(m.id);
      setFix(result);
    } catch (err) {
      if (isPlanError(err)) {
        toast.error(
          "Upgrade to get AI fixes",
          "Suggested fixes are available on the Pro plan and above."
        );
      } else {
        toast.error(
          "Could not get a suggestion",
          err instanceof Error ? err.message : undefined
        );
      }
    } finally {
      setSuggesting(false);
    }
  }

  return (
    <Card interactive className="p-4 sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              {humanize(m.source)}
            </span>
            {m.author ? (
              <span className="text-xs text-slate-400">· {m.author}</span>
            ) : null}
            {m.url ? (
              <a
                href={m.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 transition-colors hover:text-ai-indigo"
                aria-label="Open source"
              >
                <ExternalLink className="h-3.5 w-3.5" aria-hidden />
              </a>
            ) : null}
            <span className="ml-auto text-xs text-slate-400">
              {timeAgo(m.published_at || m.discovered_at)}
            </span>
          </div>
          <p className="mt-1.5 text-sm font-medium text-slate-100">
            {m.title || m.content.slice(0, 120)}
          </p>
          <p className="mt-1 line-clamp-2 text-sm text-slate-400">
            {m.analysis?.summary || m.content}
          </p>
          {m.analysis?.recommendation ? (
            <p className="mt-2 rounded-lg bg-white/[0.04] px-3 py-2 text-xs text-slate-300">
              <span className="font-medium text-slate-200">Suggested: </span>
              {m.analysis.recommendation}
            </p>
          ) : null}
        </div>

        <div className="flex shrink-0 flex-row items-center gap-2 sm:flex-col sm:items-end">
          {m.analysis ? (
            <div className="flex items-center gap-1.5 sm:flex-col sm:items-end">
              <RiskBadge level={m.analysis.risk_level} />
              <SentimentBadge sentiment={m.analysis.sentiment} />
            </div>
          ) : (
            <span className="text-xs text-slate-400">Analysis pending</span>
          )}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-white/[0.08] pt-3">
        <StatusTag status={m.status} />
        <div className="ml-auto flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            loading={suggesting}
            onClick={getSuggestion}
            leftIcon={<Sparkles className="h-3.5 w-3.5" />}
          >
            Suggest a fix
          </Button>
          {m.status !== "archived" ? (
            <Button
              size="sm"
              variant="ghost"
              loading={busy}
              onClick={() => onUpdate(m, "archived")}
              leftIcon={<Archive className="h-3.5 w-3.5" />}
            >
              Archive
            </Button>
          ) : null}
          {m.status !== "removal_requested" && m.status !== "removed" ? (
            <Button
              size="sm"
              variant="outline"
              loading={busy}
              onClick={() => onUpdate(m, "removal_requested")}
              leftIcon={<Trash2 className="h-3.5 w-3.5" />}
            >
              Request removal
            </Button>
          ) : null}
          {m.status !== "active" ? (
            <Button
              size="sm"
              variant="ghost"
              loading={busy}
              onClick={() => onUpdate(m, "active")}
              leftIcon={<RotateCcw className="h-3.5 w-3.5" />}
            >
              Restore
            </Button>
          ) : null}
        </div>
      </div>

      {fix ? <SuggestionPanel fix={fix} /> : null}
    </Card>
  );
}

function SuggestionPanel({ fix }: { fix: FixSuggestion }) {
  const isRewrite = fix.kind === "rewrite";
  return (
    <div className="mt-3 rounded-xl border border-ai-indigo/25 bg-ai-indigo/10 p-3.5">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-ai-gradient px-2.5 py-0.5 text-xs font-semibold text-white shadow-ai">
          {isRewrite ? (
            <PenLine className="h-3 w-3" aria-hidden />
          ) : (
            <Sparkles className="h-3 w-3" aria-hidden />
          )}
          {isRewrite ? "Suggested rewrite" : "Suggested response"}
        </span>
      </div>
      <p className="mt-2.5 whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
        {fix.suggestion}
      </p>
      <p className="mt-2.5 border-t border-ai-indigo/20 pt-2.5 text-xs text-slate-400">
        {fix.rationale}
      </p>
    </div>
  );
}

function StatusTag({ status }: { status: MentionStatus }) {
  const map: Record<MentionStatus, string> = {
    active: "bg-white/[0.06] text-slate-300",
    archived: "bg-white/[0.06] text-slate-400",
    removal_requested: "bg-amber-500/15 text-amber-300",
    removed: "bg-emerald-500/15 text-emerald-300",
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

function FilterPill({
  active,
  subtle = false,
  onClick,
  children,
}: {
  active: boolean;
  subtle?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full px-3 py-1.5 text-xs font-medium transition-colors",
        active
          ? subtle
            ? "bg-white/[0.10] text-white ring-1 ring-inset ring-white/[0.12]"
            : "bg-ai-gradient text-white shadow-ai"
          : "bg-white/[0.03] text-slate-300 ring-1 ring-inset ring-white/[0.10] hover:bg-white/[0.06] hover:text-slate-100"
      )}
    >
      {children}
    </button>
  );
}

function ListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <Card key={i} className="p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 space-y-2">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        </Card>
      ))}
    </div>
  );
}
