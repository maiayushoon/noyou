"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import { Check, CreditCard, ExternalLink, Loader2, Sparkles } from "lucide-react";
import { api, type BillingStatus } from "@/lib/api";
import { cn, humanize } from "@/lib/utils";
import {
  Badge,
  Button,
  Card,
  CardContent,
  Skeleton,
  Tooltip,
} from "@/components/ui";
import { useToast } from "@/lib/toast";
import { useAuth } from "@/lib/auth";
import { FadeIn } from "@/components/motion/fade-in";

interface PlanTier {
  id: "free" | "pro" | "premium" | "enterprise";
  name: string;
  price: string;
  cadence: string;
  tagline: string;
  features: string[];
  /** Enterprise routes to sales rather than self-serve checkout. */
  custom?: boolean;
  highlight?: boolean;
}

const PLANS: PlanTier[] = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    cadence: "forever",
    tagline: "Monitor your reputation and get started.",
    features: [
      "Reputation score + sentiment",
      "Manual scans",
      "1 monitored identity",
      "Community connectors",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    price: "$29",
    cadence: "/mo",
    tagline: "Predict and protect with AI on your side.",
    highlight: true,
    features: [
      "Predictive Pre-Post Check",
      "AI Visibility analysis",
      "Real platform connectors",
      "50 scans / day",
      "5 monitored identities",
    ],
  },
  {
    id: "premium",
    name: "Premium",
    price: "$59",
    cadence: "/mo",
    tagline: "Everything in Pro, scaled up with benchmarking.",
    features: [
      "Everything in Pro",
      "Competitive benchmarking",
      "500 scans / day",
      "25 monitored identities",
    ],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "Custom",
    cadence: "",
    tagline: "Unlimited scale for teams and platforms.",
    custom: true,
    features: [
      "Unlimited scans & identities",
      "API access",
      "Teams & roles",
      "Priority support & SLAs",
    ],
  },
];

export default function BillingPage() {
  const toast = useToast();
  const { refresh } = useAuth();
  const { data, error, isLoading, mutate } = useSWR<BillingStatus>(
    "billing",
    () => api.billingStatus(),
    { shouldRetryOnError: false }
  );

  const [pendingPlan, setPendingPlan] = useState<string | null>(null);
  const [portalLoading, setPortalLoading] = useState(false);

  const stripeConfigured = !!data?.publishable_key;
  const currentPlan = data?.plan ?? null;
  const hasActiveSubscription = !!data?.has_active_subscription;

  // Read ?status from the URL after returning from Stripe Checkout / Portal.
  useEffect(() => {
    const status = new URLSearchParams(window.location.search).get("status");
    if (!status) return;

    if (status === "success") {
      toast.success("Subscription active", "Your plan has been updated.");
      void refresh();
      void mutate();
    } else if (status === "cancelled") {
      toast.info("Checkout cancelled", "No changes were made to your plan.");
    }

    // Clean the query param so the toast doesn't fire again on refresh.
    const url = new URL(window.location.href);
    url.searchParams.delete("status");
    window.history.replaceState({}, "", url.toString());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function upgrade(plan: string) {
    if (!stripeConfigured) return;
    setPendingPlan(plan);
    try {
      const res = await api.billingCheckout(plan);
      window.location.href = res.url;
    } catch {
      toast.error("Could not start checkout", "Please try again in a moment.");
      setPendingPlan(null);
    }
  }

  async function manageBilling() {
    if (!stripeConfigured) return;
    setPortalLoading(true);
    try {
      const res = await api.billingPortal();
      window.location.href = res.url;
    } catch {
      toast.error("Could not open billing portal", "Please try again in a moment.");
      setPortalLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      <FadeIn>
        <Card>
          <CardContent className="flex flex-wrap items-center gap-4 py-5">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-ai-gradient text-white shadow-ai">
              <CreditCard className="h-5 w-5" aria-hidden />
            </span>
            <div className="min-w-0 flex-1">
              <h1 className="text-lg font-semibold tracking-tight text-white">
                Billing &amp; plan
              </h1>
              {isLoading || !data ? (
                <Skeleton className="mt-1.5 h-4 w-56" />
              ) : (
                <p className="mt-0.5 flex flex-wrap items-center gap-2 text-sm text-slate-400">
                  <span>You are on the</span>
                  <Badge variant={currentPlan === "free" ? "neutral" : "ai"}>
                    {humanize(currentPlan ?? "free")}
                  </Badge>
                  <span>plan.</span>
                  {data.subscription_status ? (
                    <Badge variant="outline">
                      {humanize(data.subscription_status)}
                    </Badge>
                  ) : null}
                </p>
              )}
            </div>
            {hasActiveSubscription && stripeConfigured ? (
              <Button
                variant="outline"
                loading={portalLoading}
                onClick={manageBilling}
                rightIcon={<ExternalLink className="h-4 w-4" />}
              >
                Manage billing
              </Button>
            ) : null}
          </CardContent>
        </Card>
      </FadeIn>

      {error ? (
        <FadeIn delay={0.04}>
          <Card>
            <CardContent className="py-4">
              <p className="text-sm text-slate-400">
                We couldn&apos;t load your billing details right now. The plans
                below are still available for reference.
              </p>
            </CardContent>
          </Card>
        </FadeIn>
      ) : null}

      {!isLoading && data && !stripeConfigured ? (
        <FadeIn delay={0.04}>
          <div className="flex items-start gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 py-3 text-sm text-slate-400">
            <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" aria-hidden />
            <p>
              Online payments aren&apos;t set up on this workspace yet. Plan
              upgrades will be enabled once billing is configured.
            </p>
          </div>
        </FadeIn>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {PLANS.map((plan, i) => {
          const isCurrent = currentPlan === plan.id;
          return (
            <FadeIn key={plan.id} delay={0.06 + i * 0.04} className="h-full">
              <PlanCard
                plan={plan}
                isCurrent={isCurrent}
                stripeConfigured={stripeConfigured}
                hasActiveSubscription={hasActiveSubscription}
                loading={pendingPlan === plan.id}
                anyPending={pendingPlan !== null}
                onUpgrade={() => upgrade(plan.id)}
                onManage={manageBilling}
                disabled={isLoading || !data}
              />
            </FadeIn>
          );
        })}
      </div>
    </div>
  );
}

function PlanCard({
  plan,
  isCurrent,
  stripeConfigured,
  hasActiveSubscription,
  loading,
  anyPending,
  onUpgrade,
  onManage,
  disabled,
}: {
  plan: PlanTier;
  isCurrent: boolean;
  stripeConfigured: boolean;
  hasActiveSubscription: boolean;
  loading: boolean;
  anyPending: boolean;
  onUpgrade: () => void;
  onManage: () => void;
  disabled: boolean;
}) {
  const highlighted = plan.highlight || isCurrent;

  return (
    <Card
      className={cn(
        "flex h-full flex-col",
        isCurrent && "ring-2 ring-ai-indigo",
        !isCurrent && plan.highlight && "ring-1 ring-ai-indigo/30"
      )}
    >
      <CardContent className="flex h-full flex-col gap-4 pt-5">
        <div className="flex items-center justify-between gap-2">
          <h2 className="inline-flex items-center gap-1.5 text-base font-semibold text-white">
            {plan.highlight ? (
              <Sparkles className="h-4 w-4 text-ai-violet" aria-hidden />
            ) : null}
            {plan.name}
          </h2>
          {isCurrent ? (
            <Badge variant="ai" dot>
              Current
            </Badge>
          ) : plan.highlight ? (
            <Badge variant="outline">Popular</Badge>
          ) : null}
        </div>

        <div className="flex items-baseline gap-1">
          <span className="text-2xl font-semibold tracking-tight text-white">
            {plan.price}
          </span>
          {plan.cadence ? (
            <span className="text-sm text-slate-400">{plan.cadence}</span>
          ) : null}
        </div>

        <p className="text-sm text-slate-400">{plan.tagline}</p>

        <ul className="space-y-2">
          {plan.features.map((f) => (
            <li key={f} className="flex items-start gap-2 text-sm text-slate-300">
              <Check
                className={cn(
                  "mt-0.5 h-4 w-4 shrink-0",
                  highlighted ? "text-ai-violet" : "text-emerald-500"
                )}
                aria-hidden
              />
              <span>{f}</span>
            </li>
          ))}
        </ul>

        <div className="mt-auto pt-2">
          <PlanAction
            plan={plan}
            isCurrent={isCurrent}
            stripeConfigured={stripeConfigured}
            hasActiveSubscription={hasActiveSubscription}
            loading={loading}
            anyPending={anyPending}
            onUpgrade={onUpgrade}
            onManage={onManage}
            disabled={disabled}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function PlanAction({
  plan,
  isCurrent,
  stripeConfigured,
  hasActiveSubscription,
  loading,
  anyPending,
  onUpgrade,
  onManage,
  disabled,
}: {
  plan: PlanTier;
  isCurrent: boolean;
  stripeConfigured: boolean;
  hasActiveSubscription: boolean;
  loading: boolean;
  anyPending: boolean;
  onUpgrade: () => void;
  onManage: () => void;
  disabled: boolean;
}) {
  // Current plan: offer portal management for paid subscribers, otherwise a static state.
  if (isCurrent) {
    if (hasActiveSubscription && stripeConfigured) {
      return (
        <Button
          variant="outline"
          className="w-full"
          onClick={onManage}
          rightIcon={<ExternalLink className="h-4 w-4" />}
        >
          Manage billing
        </Button>
      );
    }
    return (
      <Button variant="secondary" className="w-full" disabled>
        Current plan
      </Button>
    );
  }

  // Enterprise: contact sales (mailto), always available.
  if (plan.custom) {
    return (
      <a href="mailto:sales@noyou.app?subject=NoYou%20Enterprise" className="block">
        <Button
          variant="outline"
          className="w-full"
          rightIcon={<ExternalLink className="h-4 w-4" />}
        >
          Contact sales
        </Button>
      </a>
    );
  }

  // Free downgrade is handled in the billing portal, not via checkout.
  if (plan.id === "free") {
    if (hasActiveSubscription && stripeConfigured) {
      return (
        <Button variant="outline" className="w-full" onClick={onManage}>
          Manage in portal
        </Button>
      );
    }
    return (
      <Button variant="ghost" className="w-full" disabled>
        Included
      </Button>
    );
  }

  // Paid self-serve upgrade.
  const upgradeButton = (
    <Button
      variant="ai"
      className="w-full"
      loading={loading}
      disabled={disabled || !stripeConfigured || (anyPending && !loading)}
      onClick={onUpgrade}
    >
      {loading ? null : <Sparkles className="h-4 w-4" aria-hidden />}
      Upgrade to {plan.name}
    </Button>
  );

  if (!stripeConfigured) {
    // Tooltip's trigger is inline-flex, so wrap the disabled button in a
    // full-width block to preserve its w-full sizing inside the card.
    return (
      <div className="[&_>span]:w-full [&_span]:w-full">
        <Tooltip content="Billing isn't set up on this workspace yet">
          {upgradeButton}
        </Tooltip>
      </div>
    );
  }

  return upgradeButton;
}
