"use client";

import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Send,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  XCircle,
} from "lucide-react";
import {
  api,
  type AnalyzeResult,
  type PublishRecommendation,
} from "@/lib/api";
import { cn, riskColor } from "@/lib/utils";
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  PlanGate,
  RiskBadge,
  SentimentBadge,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn } from "@/components/motion/fade-in";

const SAMPLES = [
  "Honestly the support team at this company is a joke, total waste of money.",
  "Excited to share that we just shipped our biggest release yet — thank you all!",
  "I can't believe they did this to me. Never trusting them again.",
];

const VERDICT: Record<
  PublishRecommendation,
  { label: string; icon: typeof CheckCircle2; tone: string; ring: string }
> = {
  safe_to_post: {
    label: "Safe to post",
    icon: CheckCircle2,
    tone: "text-emerald-300",
    ring: "bg-emerald-500/10 ring-emerald-500/30",
  },
  review_suggested: {
    label: "Review suggested",
    icon: AlertTriangle,
    tone: "text-amber-300",
    ring: "bg-amber-500/10 ring-amber-500/30",
  },
  do_not_post: {
    label: "Do not post",
    icon: XCircle,
    tone: "text-red-300",
    ring: "bg-red-500/10 ring-red-500/30",
  },
};

export default function PredictPage() {
  const [text, setText] = useState("");
  const [context, setContext] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const r = await api.analyze({ text, context: context || undefined });
      setResult(r);
    } catch (err) {
      setError(err);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Pre-Post Check"
        description="Run any draft through AI before you publish to gauge reputation risk."
        actions={
          <Badge variant="ai" dot dotClassName="bg-white">
            AI
          </Badge>
        }
      />

      <PlanGate error={error} feature="pre_post_check">
        <div className="grid gap-6 lg:grid-cols-2">
          <FadeIn>
            <Card>
              <CardHeader>
                <CardTitle>Your draft</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={7}
                  placeholder="Paste the post, reply, or message you're about to publish…"
                  className="w-full resize-y rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
                />
                <input
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="Optional: where will this be posted? (e.g. LinkedIn, a reply to a critic)"
                  className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
                />
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    variant="ai"
                    onClick={run}
                    loading={loading}
                    disabled={!text.trim()}
                    leftIcon={!loading ? <Send className="h-4 w-4" /> : undefined}
                  >
                    {loading ? "Analyzing…" : "Check before posting"}
                  </Button>
                  <span className="text-xs text-slate-400">
                    {text.length} characters
                  </span>
                </div>
                <div className="border-t border-white/[0.08] pt-3">
                  <p className="mb-2 text-xs font-medium text-slate-400">
                    Try an example
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {SAMPLES.map((s, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => setText(s)}
                        className="rounded-full bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-slate-300 ring-1 ring-inset ring-white/[0.10] transition-colors hover:bg-white/[0.06]"
                      >
                        Example {i + 1}
                      </button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn delay={0.05}>
            {result ? (
              <ResultCard result={result} />
            ) : (
              <Card className="flex h-full flex-col items-center justify-center px-6 py-16 text-center">
                <span className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-ai-gradient-soft text-indigo-300 ring-1 ring-inset ring-white/[0.08]">
                  <Sparkles className="h-6 w-6" aria-hidden />
                </span>
                <p className="text-sm font-semibold text-slate-100">
                  Your reputation forecast appears here
                </p>
                <p className="mt-1 max-w-xs text-sm text-slate-400">
                  We score sentiment, risk, and whether a draft is safe to post —
                  before anyone else sees it.
                </p>
              </Card>
            )}
          </FadeIn>
        </div>
      </PlanGate>
    </div>
  );
}

function ResultCard({ result }: { result: AnalyzeResult }) {
  const v = VERDICT[result.publish_recommendation] ?? VERDICT.review_suggested;
  const VIcon = v.icon;
  const risk = riskColor(result.risk_level);

  return (
    <Card className="overflow-hidden">
      <div className={cn("flex items-center gap-3 px-5 py-4 ring-1 ring-inset", v.ring)}>
        <VIcon className={cn("h-6 w-6 shrink-0", v.tone)} aria-hidden />
        <div>
          <p className={cn("text-sm font-semibold", v.tone)}>{v.label}</p>
          <p className="text-xs text-slate-400">
            Confidence {Math.round(result.confidence * 100)}% · via {result.analyzer}
          </p>
        </div>
      </div>
      <CardContent className="space-y-4 pt-5">
        <div className="flex flex-wrap items-center gap-2">
          <SentimentBadge sentiment={result.sentiment} />
          <RiskBadge level={result.risk_level} />
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium",
              risk.bg,
              risk.text,
              risk.border
            )}
          >
            {result.risk_category.replace(/_/g, " ")}
          </span>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Summary
          </p>
          <p className="mt-1 text-sm text-slate-300">{result.summary}</p>
        </div>

        <div className="rounded-lg border border-white/[0.06] bg-white/[0.04] px-3 py-2.5">
          <p className="flex items-center gap-1.5 text-xs font-medium text-slate-200">
            {result.risk_level >= 3 ? (
              <ShieldAlert className="h-3.5 w-3.5 text-amber-300" aria-hidden />
            ) : (
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-300" aria-hidden />
            )}
            Recommendation
          </p>
          <p className="mt-1 text-sm text-slate-300">{result.recommendation}</p>
        </div>

        {result.flagged_terms.length > 0 ? (
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Flagged language
            </p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {result.flagged_terms.map((t) => (
                <span
                  key={t}
                  className="rounded-md bg-red-500/15 px-2 py-0.5 text-xs font-medium text-red-300 ring-1 ring-inset ring-red-500/30"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
