"use client";

import { useState } from "react";
import Link from "next/link";
import useSWR, { useSWRConfig } from "swr";
import {
  AtSign,
  CreditCard,
  ExternalLink,
  Plus,
  Trash2,
  UserRound,
} from "lucide-react";
import { api, type Account } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cn, humanize } from "@/lib/utils";
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

const PLATFORMS = [
  "web",
  "twitter",
  "reddit",
  "youtube",
  "google",
  "hackernews",
  "linkedin",
] as const;

const PLATFORM_LABEL: Record<string, string> = {
  web: "Web / Blogs",
  twitter: "X (Twitter)",
  reddit: "Reddit",
  youtube: "YouTube",
  google: "Google",
  hackernews: "Hacker News",
  linkedin: "LinkedIn",
};

export default function AccountsPage() {
  const toast = useToast();
  const { user } = useAuth();
  const { mutate } = useSWRConfig();
  const { data, error, isLoading } = useSWR<Account[]>("accounts", () =>
    api.listAccounts()
  );

  const [platform, setPlatform] = useState<string>("web");
  const [handle, setHandle] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [profileUrl, setProfileUrl] = useState("");
  const [adding, setAdding] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);

  const accounts = data ?? [];

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!handle.trim()) return;
    setAdding(true);
    try {
      await api.createAccount({
        platform,
        handle: handle.trim(),
        display_name: displayName.trim() || undefined,
        profile_url: profileUrl.trim() || undefined,
      });
      setHandle("");
      setDisplayName("");
      setProfileUrl("");
      mutate("accounts");
      toast.success("Identity added", "We'll include it in your next scan.");
    } catch (err) {
      toast.error("Could not add identity", err instanceof Error ? err.message : undefined);
    } finally {
      setAdding(false);
    }
  }

  async function remove(a: Account) {
    setBusyId(String(a.id));
    try {
      await api.deleteAccount(a.id);
      mutate("accounts");
      toast.success("Identity removed");
    } catch (err) {
      toast.error("Could not remove identity", err instanceof Error ? err.message : undefined);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Accounts"
        description="Connect the identities and profiles NoYou should monitor for you."
      />

      {/* Plan summary */}
      <FadeIn>
        <Card className="mb-6 flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-ai-gradient-soft text-ai-violet">
              <CreditCard className="h-5 w-5" aria-hidden />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">
                Current plan
                <Badge variant={user?.plan === "free" ? "neutral" : "ai"} className="ml-2">
                  {humanize(user?.plan ?? "free")}
                </Badge>
              </p>
              <p className="mt-0.5 text-sm text-slate-500">
                Manage your subscription, invoices, and payment method.
              </p>
            </div>
          </div>
          <Link href="/billing">
            <Button variant="outline" rightIcon={<ExternalLink className="h-4 w-4" />}>
              Manage billing
            </Button>
          </Link>
        </Card>
      </FadeIn>

      <div className="grid gap-6 lg:grid-cols-[1fr,1.4fr]">
        {/* Add form */}
        <FadeIn>
          <Card>
            <CardHeader>
              <CardTitle>Add an identity to monitor</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={add} className="space-y-3.5">
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-slate-700">
                    Platform
                  </label>
                  <select
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/20"
                  >
                    {PLATFORMS.map((p) => (
                      <option key={p} value={p}>
                        {PLATFORM_LABEL[p]}
                      </option>
                    ))}
                  </select>
                </div>
                <Field
                  label="Handle or name"
                  icon={<AtSign className="h-4 w-4" />}
                  value={handle}
                  onChange={setHandle}
                  placeholder="your-name or @handle"
                  required
                />
                <Field
                  label="Display name (optional)"
                  value={displayName}
                  onChange={setDisplayName}
                  placeholder="How it should appear"
                />
                <Field
                  label="Profile URL (optional)"
                  value={profileUrl}
                  onChange={setProfileUrl}
                  placeholder="https://…"
                  type="url"
                />
                <Button
                  type="submit"
                  variant="ai"
                  className="w-full"
                  loading={adding}
                  disabled={!handle.trim()}
                  leftIcon={!adding ? <Plus className="h-4 w-4" /> : undefined}
                >
                  Add identity
                </Button>
              </form>
            </CardContent>
          </Card>
        </FadeIn>

        {/* List */}
        <FadeIn delay={0.05}>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Monitored identities</CardTitle>
              <span className="text-xs text-slate-400">
                {isLoading ? "…" : `${accounts.length} total`}
              </span>
            </CardHeader>
            <CardContent className="pt-0">
              {isLoading ? (
                <div className="space-y-2.5 pt-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-16 w-full rounded-lg" />
                  ))}
                </div>
              ) : error ? (
                <EmptyState
                  icon={<UserRound className="h-5 w-5" />}
                  title="Could not load identities"
                  description="The API may be unreachable. Try refreshing."
                />
              ) : accounts.length === 0 ? (
                <EmptyState
                  icon={<UserRound className="h-5 w-5" />}
                  title="No identities yet"
                  description="Add your name, brand, or handles so NoYou knows what to watch."
                />
              ) : (
                <StaggerList className="space-y-2.5">
                  {accounts.map((a) => (
                    <FadeInItem key={String(a.id)}>
                      <div className="flex items-center gap-3 rounded-lg border border-hairline p-3.5">
                        <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                          <AtSign className="h-4 w-4" aria-hidden />
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <p className="truncate text-sm font-medium text-slate-900">
                              {a.display_name || a.handle}
                            </p>
                            <span
                              className={cn(
                                "shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500",
                                !a.is_active && "opacity-60"
                              )}
                            >
                              {PLATFORM_LABEL[a.platform] || humanize(a.platform)}
                            </span>
                          </div>
                          <p className="truncate text-xs text-slate-400">{a.handle}</p>
                        </div>
                        {a.profile_url ? (
                          <a
                            href={a.profile_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-slate-400 transition-colors hover:text-ai-indigo"
                            aria-label="Open profile"
                          >
                            <ExternalLink className="h-4 w-4" aria-hidden />
                          </a>
                        ) : null}
                        <Button
                          size="icon"
                          variant="ghost"
                          loading={busyId === String(a.id)}
                          onClick={() => remove(a)}
                          aria-label="Remove identity"
                        >
                          <Trash2 className="h-4 w-4 text-slate-400" />
                        </Button>
                      </div>
                    </FadeInItem>
                  ))}
                </StaggerList>
              )}
            </CardContent>
          </Card>
        </FadeIn>
      </div>
    </div>
  );
}

function Field({
  label,
  icon,
  value,
  onChange,
  placeholder,
  type = "text",
  required = false,
}: {
  label: string;
  icon?: React.ReactNode;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-700">{label}</label>
      <div className="relative">
        {icon ? (
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            {icon}
          </span>
        ) : null}
        <input
          type={type}
          required={required}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={cn(
            "w-full rounded-lg border border-slate-200 bg-white py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/20",
            icon ? "pl-9 pr-3" : "px-3"
          )}
        />
      </div>
    </div>
  );
}
