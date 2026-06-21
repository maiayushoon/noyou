"use client";

import { useEffect, useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import {
  Building2,
  Crown,
  Mail,
  Plus,
  Trash2,
  UserPlus,
  Users,
} from "lucide-react";
import {
  api,
  type Organization,
  type OrgMember,
  isPlanError,
} from "@/lib/api";
import { cn, humanize } from "@/lib/utils";
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  EmptyState,
  PlanGate,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { useToast } from "@/lib/toast";

export default function TeamsPage() {
  const toast = useToast();
  const { mutate } = useSWRConfig();
  const [orgName, setOrgName] = useState("");
  const [creating, setCreating] = useState(false);
  const [activeOrg, setActiveOrg] = useState<string | null>(null);

  const orgs = useSWR<Organization[]>("orgs", () => api.listOrgs());

  // Default the selected org to the first one once loaded.
  useEffect(() => {
    const first = orgs.data?.[0];
    if (!activeOrg && first) {
      setActiveOrg(String(first.id));
    }
  }, [orgs.data, activeOrg]);

  async function createOrg(e: React.FormEvent) {
    e.preventDefault();
    if (!orgName.trim()) return;
    setCreating(true);
    try {
      const created = await api.createOrg({ name: orgName.trim() });
      setOrgName("");
      await mutate("orgs");
      setActiveOrg(String(created.id));
      toast.success("Organization created");
    } catch (err) {
      if (isPlanError(err)) {
        toast.error("Teams is a Pro feature", "Upgrade to collaborate with your team.");
      } else {
        toast.error("Could not create organization", err instanceof Error ? err.message : undefined);
      }
    } finally {
      setCreating(false);
    }
  }

  const gateError = isPlanError(orgs.error) ? orgs.error : null;
  const selected = orgs.data?.find((o) => String(o.id) === activeOrg) ?? null;

  return (
    <div>
      <PageHeader
        title="Teams"
        description="Bring your agency or team into one workspace with shared monitoring."
        actions={
          <Badge variant="ai" dot dotClassName="bg-white">
            Pro
          </Badge>
        }
      />

      <PlanGate error={gateError} feature="teams">
        <div className="grid gap-6 lg:grid-cols-[1fr,1.6fr]">
          {/* Orgs list + create */}
          <FadeIn>
            <Card>
              <CardHeader>
                <CardTitle>Your organizations</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={createOrg} className="flex gap-2">
                  <input
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    placeholder="New organization name"
                    className="min-w-0 flex-1 rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
                  />
                  <Button
                    type="submit"
                    variant="ai"
                    loading={creating}
                    disabled={!orgName.trim()}
                    leftIcon={!creating ? <Plus className="h-4 w-4" /> : undefined}
                  >
                    Create
                  </Button>
                </form>

                <div className="mt-4">
                  {orgs.isLoading ? (
                    <div className="space-y-2">
                      {Array.from({ length: 2 }).map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full rounded-lg" />
                      ))}
                    </div>
                  ) : (orgs.data?.length ?? 0) === 0 ? (
                    <p className="py-6 text-center text-sm text-slate-400">
                      No organizations yet. Create one to invite teammates.
                    </p>
                  ) : (
                    <StaggerList className="space-y-2">
                      {orgs.data!.map((o) => (
                        <FadeInItem key={String(o.id)}>
                          <button
                            type="button"
                            onClick={() => setActiveOrg(String(o.id))}
                            className={cn(
                              "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors",
                              String(o.id) === activeOrg
                                ? "border-ai-indigo/40 bg-ai-gradient-soft shadow-[0_0_40px_-12px_rgba(139,92,246,0.45)]"
                                : "border-white/[0.08] bg-white/[0.03] hover:border-white/[0.12] hover:bg-white/[0.06]"
                            )}
                          >
                            <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/[0.06] text-indigo-300 ring-1 ring-inset ring-white/[0.10]">
                              <Building2 className="h-4 w-4" aria-hidden />
                            </span>
                            <div className="min-w-0 flex-1">
                              <p className="truncate text-sm font-medium text-slate-100">
                                {o.name}
                              </p>
                              <p className="text-xs capitalize text-slate-400">{o.role}</p>
                            </div>
                            {o.role === "owner" ? (
                              <Crown className="h-3.5 w-3.5 text-amber-400" aria-hidden />
                            ) : null}
                          </button>
                        </FadeInItem>
                      ))}
                    </StaggerList>
                  )}
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          {/* Members of selected org */}
          <FadeIn delay={0.05}>
            {selected ? (
              <MembersCard org={selected} />
            ) : (
              <Card className="flex h-full flex-col items-center justify-center px-6 py-16 text-center">
                <span className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-ai-gradient-soft text-indigo-300 ring-1 ring-inset ring-white/[0.08]">
                  <Users className="h-6 w-6" aria-hidden />
                </span>
                <p className="text-sm font-semibold text-slate-100">Select an organization</p>
                <p className="mt-1 max-w-xs text-sm text-slate-400">
                  Create or choose an organization to manage its members.
                </p>
              </Card>
            )}
          </FadeIn>
        </div>
      </PlanGate>
    </div>
  );
}

function MembersCard({ org }: { org: Organization }) {
  const toast = useToast();
  const { mutate } = useSWRConfig();
  const [email, setEmail] = useState("");
  const [inviting, setInviting] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const isOwner = org.role === "owner";

  const key = `members:${org.id}`;
  const { data, error, isLoading } = useSWR<OrgMember[]>(key, () =>
    api.listMembers(org.id)
  );

  async function invite(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setInviting(true);
    try {
      await api.inviteMember(org.id, { email: email.trim() });
      setEmail("");
      mutate(key);
      toast.success("Invitation sent", `${email.trim()} can now join ${org.name}.`);
    } catch (err) {
      toast.error("Could not invite member", err instanceof Error ? err.message : undefined);
    } finally {
      setInviting(false);
    }
  }

  async function remove(m: OrgMember) {
    setBusyId(String(m.id));
    try {
      await api.removeMember(org.id, m.id);
      mutate(key);
      toast.success("Member removed");
    } catch (err) {
      toast.error("Could not remove member", err instanceof Error ? err.message : undefined);
    } finally {
      setBusyId(null);
    }
  }

  const members = data ?? [];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>{org.name} · members</CardTitle>
        <span className="text-xs text-slate-400">
          {isLoading ? "…" : `${members.length} member${members.length === 1 ? "" : "s"}`}
        </span>
      </CardHeader>
      <CardContent>
        {isOwner ? (
          <form onSubmit={invite} className="flex gap-2">
            <div className="relative min-w-0 flex-1">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                <Mail className="h-4 w-4" aria-hidden />
              </span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="teammate@company.com"
                className="w-full rounded-lg border border-white/10 bg-white/[0.04] py-2.5 pl-9 pr-3 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-ai-indigo focus:ring-2 focus:ring-ai-indigo/30"
              />
            </div>
            <Button
              type="submit"
              variant="ai"
              loading={inviting}
              disabled={!email.trim()}
              leftIcon={!inviting ? <UserPlus className="h-4 w-4" /> : undefined}
            >
              Invite
            </Button>
          </form>
        ) : (
          <p className="rounded-lg bg-white/[0.04] px-3 py-2.5 text-xs text-slate-400">
            Only the organization owner can invite or remove members.
          </p>
        )}

        <div className="mt-4">
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full rounded-lg" />
              ))}
            </div>
          ) : error ? (
            <EmptyState
              icon={<Users className="h-5 w-5" />}
              title="Could not load members"
              description="The API may be unreachable. Try refreshing."
            />
          ) : members.length === 0 ? (
            <EmptyState
              icon={<Users className="h-5 w-5" />}
              title="No members yet"
              description="Invite teammates by email to collaborate here."
            />
          ) : (
            <StaggerList className="space-y-2">
              {members.map((m) => (
                <FadeInItem key={String(m.id)}>
                  <div className="flex items-center gap-3 rounded-lg border border-white/[0.08] bg-white/[0.03] p-3 transition-colors hover:border-white/[0.12]">
                    <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ai-gradient-soft text-sm font-semibold text-indigo-300 ring-1 ring-inset ring-white/[0.08]">
                      {m.email.charAt(0).toUpperCase()}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-slate-100">{m.email}</p>
                      <p className="text-xs capitalize text-slate-400">{humanize(m.role)}</p>
                    </div>
                    <span
                      className={cn(
                        "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
                        m.status === "active"
                          ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                          : "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                      )}
                    >
                      {humanize(m.status)}
                    </span>
                    {isOwner && m.role !== "owner" ? (
                      <Button
                        size="icon"
                        variant="ghost"
                        loading={busyId === String(m.id)}
                        onClick={() => remove(m)}
                        aria-label="Remove member"
                      >
                        <Trash2 className="h-4 w-4 text-slate-400" />
                      </Button>
                    ) : null}
                  </div>
                </FadeInItem>
              ))}
            </StaggerList>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
