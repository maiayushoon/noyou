"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import useSWR, { useSWRConfig } from "swr";
import {
  AtSign,
  CheckCircle2,
  Globe,
  Link2,
  Lock,
  Server,
  Sparkles,
  Unplug,
  type LucideIcon,
} from "lucide-react";
import {
  api,
  isPlanError,
  type Connection,
  type ConnectionProvider,
  type ConnectionStatus,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cn, humanize, timeAgo } from "@/lib/utils";
import {
  Badge,
  Button,
  Card,
  CardContent,
  EmptyState,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { useToast } from "@/lib/toast";

/* ------------------------------ Presentation ------------------------------ */

const PROVIDER_ICON: Record<string, LucideIcon> = {
  twitter: AtSign,
  x: AtSign,
  mastodon: Server,
  reddit: Globe,
  linkedin: Globe,
  github: Globe,
  google: Globe,
  youtube: Globe,
  bluesky: AtSign,
  threads: AtSign,
};

function providerIcon(provider: string): LucideIcon {
  return PROVIDER_ICON[provider.toLowerCase()] ?? Link2;
}

const STATUS_STYLE: Record<
  ConnectionStatus,
  { label: string; pill: string; dot: string }
> = {
  connected: {
    label: "Connected",
    pill: "bg-emerald-500/15 text-emerald-300 ring-1 ring-inset ring-emerald-500/30",
    dot: "bg-emerald-400",
  },
  expired: {
    label: "Expired",
    pill: "bg-amber-500/15 text-amber-300 ring-1 ring-inset ring-amber-500/30",
    dot: "bg-amber-400",
  },
  revoked: {
    label: "Revoked",
    pill: "bg-white/[0.06] text-slate-400 ring-1 ring-inset ring-white/[0.10]",
    dot: "bg-slate-500",
  },
  error: {
    label: "Needs attention",
    pill: "bg-red-500/15 text-red-300 ring-1 ring-inset ring-red-500/30",
    dot: "bg-red-400",
  },
};

const NOT_CONNECTED = {
  label: "Not connected",
  pill: "bg-white/[0.06] text-slate-400 ring-1 ring-inset ring-white/[0.10]",
  dot: "bg-slate-500",
};

/* --------------------------------- Page ---------------------------------- */

export default function ConnectionsPage() {
  const toast = useToast();
  const { user } = useAuth();
  const { mutate } = useSWRConfig();

  const {
    data: providers,
    error: providersError,
    isLoading: providersLoading,
  } = useSWR<ConnectionProvider[]>("connection-providers", () =>
    api.connectionProviders()
  );
  const { data: connections, isLoading: connectionsLoading } = useSWR<
    Connection[]
  >("connections", () => api.listConnections());

  // After the backend OAuth callback redirects back, read ?connected / ?error.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const connected = params.get("connected");
    const errored = params.get("error");
    if (!connected && !errored) return;

    if (connected) {
      toast.success(
        "Account connected",
        `${humanize(connected)} is now linked to NoYou.`
      );
    } else if (errored) {
      toast.error(
        "Could not connect",
        errored === "1" || errored === "true"
          ? "The connection was cancelled or failed. Please try again."
          : humanize(errored)
      );
    }

    void mutate("connections");
    void mutate("connection-providers");

    const url = new URL(window.location.href);
    url.searchParams.delete("connected");
    url.searchParams.delete("error");
    window.history.replaceState({}, "", url.toString());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isLoading = providersLoading || connectionsLoading;
  const list = providers ?? [];

  // Map provider key -> active connection (if any).
  const byProvider = new Map<string, Connection>();
  for (const c of connections ?? []) {
    const existing = byProvider.get(c.provider);
    // Prefer a healthy connection over a stale one if duplicates exist.
    if (!existing || (existing.status !== "connected" && c.status === "connected")) {
      byProvider.set(c.provider, c);
    }
  }

  return (
    <div>
      <PageHeader
        title="Connections"
        description="Link your own accounts so NoYou can act on your behalf and pull deeper signals."
      />

      {/* Plan banner — mirrors the Accounts page summary card. */}
      <FadeIn>
        <Card className="mb-6 flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-ai-gradient-soft text-ai-violet">
              <Link2 className="h-5 w-5" aria-hidden />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-100">
                Account linking
                <Badge
                  variant={user?.plan === "free" ? "neutral" : "ai"}
                  className="ml-2"
                >
                  {humanize(user?.plan ?? "free")}
                </Badge>
              </p>
              <p className="mt-0.5 text-sm text-slate-400">
                {user?.plan === "free"
                  ? "Connecting your own accounts is a Pro feature."
                  : "Securely connect platforms via OAuth. You can disconnect anytime."}
              </p>
            </div>
          </div>
          {user?.plan === "free" ? (
            <Link href="/billing">
              <Button variant="ai" leftIcon={<Sparkles className="h-4 w-4" />}>
                Upgrade to connect
              </Button>
            </Link>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400">
              <Lock className="h-3.5 w-3.5" aria-hidden />
              OAuth secured
            </span>
          )}
        </Card>
      </FadeIn>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 w-full rounded-xl" />
          ))}
        </div>
      ) : providersError ? (
        <Card>
          {isPlanError(providersError) ? (
            <EmptyState
              icon={<Sparkles className="h-5 w-5" />}
              title="Connecting accounts is a Pro feature"
              description="Upgrade to link your own accounts and pull first-party signals into your scans."
              action={
                <Link href="/billing">
                  <Button variant="ai" leftIcon={<Sparkles className="h-4 w-4" />}>
                    Upgrade plan
                  </Button>
                </Link>
              }
            />
          ) : (
            <EmptyState
              icon={<Unplug className="h-5 w-5" />}
              title="Could not load providers"
              description="The API may be unreachable. Try refreshing the page."
            />
          )}
        </Card>
      ) : list.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Link2 className="h-5 w-5" />}
            title="No providers available"
            description="No connectable platforms are configured yet. Check back soon."
          />
        </Card>
      ) : (
        <StaggerList className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {list.map((provider) => (
            <FadeInItem key={provider.provider}>
              <ProviderCard
                provider={provider}
                connection={byProvider.get(provider.provider) ?? null}
                onChanged={() => {
                  void mutate("connections");
                  void mutate("connection-providers");
                }}
              />
            </FadeInItem>
          ))}
        </StaggerList>
      )}
    </div>
  );
}

/* ------------------------------ Provider card ----------------------------- */

function ProviderCard({
  provider,
  connection,
  onChanged,
}: {
  provider: ConnectionProvider;
  connection: Connection | null;
  onChanged: () => void;
}) {
  const toast = useToast();
  const Icon = providerIcon(provider.provider);
  const isConnected = !!connection && connection.status !== "revoked";
  const status = connection
    ? STATUS_STYLE[connection.status]
    : NOT_CONNECTED;

  const isMastodon = provider.provider.toLowerCase() === "mastodon";
  const [showInstance, setShowInstance] = useState(false);
  const [instanceUrl, setInstanceUrl] = useState("");
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);

  const scopes =
    (connection?.scopes?.length ? connection.scopes : provider.scopes_requested) ??
    [];

  async function startConnect() {
    if (isMastodon && !showInstance) {
      setShowInstance(true);
      return;
    }
    if (isMastodon && !instanceUrl.trim()) {
      toast.error("Instance required", "Enter your Mastodon instance URL.");
      return;
    }
    setConnecting(true);
    try {
      const { authorize_url } = await api.connectProvider(
        provider.provider,
        isMastodon ? instanceUrl.trim() : undefined
      );
      // Hand off to the provider's OAuth consent screen.
      window.location.href = authorize_url;
    } catch (err) {
      // 402 PlanError already surfaces an upgrade-prompt toast via request().
      toast.error(
        "Could not start connection",
        err instanceof Error ? err.message : undefined
      );
      setConnecting(false);
    }
  }

  async function handleDisconnect() {
    if (!connection) return;
    if (
      !window.confirm(
        `Disconnect ${provider.label}? NoYou will stop accessing this account.`
      )
    ) {
      return;
    }
    setDisconnecting(true);
    try {
      await api.disconnect(connection.id);
      toast.success(`${provider.label} disconnected`);
      onChanged();
    } catch (err) {
      toast.error(
        "Could not disconnect",
        err instanceof Error ? err.message : undefined
      );
    } finally {
      setDisconnecting(false);
    }
  }

  return (
    <Card className="flex h-full flex-col" interactive>
      <CardContent className="flex flex-1 flex-col p-5">
        {/* Header: icon + label + status pill */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span
              className={cn(
                "inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                isConnected
                  ? "bg-ai-gradient-soft text-indigo-300 ring-1 ring-inset ring-white/[0.08]"
                  : "bg-white/[0.06] text-slate-400"
              )}
            >
              <Icon className="h-5 w-5" aria-hidden />
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-100">
                {provider.label || humanize(provider.provider)}
              </p>
              {connection?.external_handle || connection?.display_name ? (
                <p className="truncate text-xs text-slate-400">
                  {connection.display_name || connection.external_handle}
                </p>
              ) : (
                <p className="truncate text-xs text-slate-400">
                  {humanize(provider.provider)}
                </p>
              )}
            </div>
          </div>
          <span
            className={cn(
              "inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
              status.pill
            )}
          >
            <span
              className={cn("h-1.5 w-1.5 rounded-full", status.dot)}
              aria-hidden
            />
            {status.label}
          </span>
        </div>

        {/* Connected detail: handle, scopes, last synced */}
        {isConnected && connection ? (
          <div className="mt-4 space-y-3">
            {connection.external_handle ? (
              <p className="flex items-center gap-1.5 text-sm text-slate-300">
                <AtSign className="h-3.5 w-3.5 text-slate-400" aria-hidden />
                <span className="truncate">{connection.external_handle}</span>
              </p>
            ) : null}
            {scopes.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {scopes.map((scope) => (
                  <span
                    key={scope}
                    className="rounded-md bg-white/[0.06] px-1.5 py-0.5 text-[0.7rem] font-medium text-slate-400"
                  >
                    {scope}
                  </span>
                ))}
              </div>
            ) : null}
            <p className="flex items-center gap-1.5 text-xs text-slate-400">
              <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />
              Last synced {timeAgo(connection.last_synced_at)}
            </p>
          </div>
        ) : (
          <div className="mt-4">
            {scopes.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {scopes.map((scope) => (
                  <span
                    key={scope}
                    className="rounded-md bg-white/[0.06] px-1.5 py-0.5 text-[0.7rem] font-medium text-slate-500"
                  >
                    {scope}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">
                Connect to grant access and start syncing.
              </p>
            )}
          </div>
        )}

        {/* Mastodon instance input, revealed before connecting */}
        {!isConnected && isMastodon && showInstance ? (
          <div className="mt-3">
            <label className="mb-1.5 block text-xs font-medium text-slate-300">
              Mastodon instance
            </label>
            <input
              type="url"
              autoFocus
              value={instanceUrl}
              onChange={(e) => setInstanceUrl(e.target.value)}
              placeholder="https://mastodon.social"
              className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
            />
          </div>
        ) : null}

        {/* Actions */}
        <div className="mt-auto pt-5">
          {isConnected ? (
            <Button
              variant="outline"
              className="w-full"
              loading={disconnecting}
              onClick={handleDisconnect}
              leftIcon={
                !disconnecting ? <Unplug className="h-4 w-4" /> : undefined
              }
            >
              Disconnect
            </Button>
          ) : provider.configured ? (
            <Button
              variant="ai"
              className="w-full"
              loading={connecting}
              onClick={startConnect}
              leftIcon={
                !connecting ? <Link2 className="h-4 w-4" /> : undefined
              }
            >
              {isMastodon && !showInstance ? "Connect…" : "Connect"}
            </Button>
          ) : (
            <div className="flex flex-col items-center gap-1.5">
              <Button variant="outline" className="w-full" disabled>
                Connect
              </Button>
              <span className="inline-flex items-center gap-1.5 text-[0.7rem] font-medium text-slate-500">
                <Lock className="h-3 w-3" aria-hidden />
                Needs setup
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
