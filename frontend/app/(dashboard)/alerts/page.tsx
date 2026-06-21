"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import { Bell, BellOff, Check, CheckCheck } from "lucide-react";
import { api, type Alert } from "@/lib/api";
import { cn, severityColor, timeAgo } from "@/lib/utils";
import {
  Button,
  Card,
  EmptyState,
  Skeleton,
} from "@/components/ui";
import { PageHeader } from "@/components/layout/page-header";
import { FadeIn, FadeInItem, StaggerList } from "@/components/motion/fade-in";
import { useToast } from "@/lib/toast";

export default function AlertsPage() {
  const toast = useToast();
  const { mutate } = useSWRConfig();
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [markingAll, setMarkingAll] = useState(false);

  const key = `alerts:${unreadOnly}`;
  const { data, error, isLoading } = useSWR<Alert[]>(key, () =>
    api.listAlerts({ unread_only: unreadOnly || undefined, limit: 100 })
  );

  const alerts = data ?? [];
  const unreadCount = alerts.filter((a) => !a.is_read).length;

  function refresh() {
    mutate((k) => typeof k === "string" && k.startsWith("alerts"));
    mutate("dashboard");
  }

  async function markRead(a: Alert) {
    if (a.is_read) return;
    setBusyId(String(a.id));
    try {
      await api.markAlertRead(a.id);
      refresh();
    } catch (err) {
      toast.error("Could not mark as read", err instanceof Error ? err.message : undefined);
    } finally {
      setBusyId(null);
    }
  }

  async function markAll() {
    setMarkingAll(true);
    try {
      await api.markAllAlertsRead();
      refresh();
      toast.success("All alerts marked as read");
    } catch (err) {
      toast.error("Could not update alerts", err instanceof Error ? err.message : undefined);
    } finally {
      setMarkingAll(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Alerts"
        description="Real-time notifications when something about your reputation needs attention."
        actions={
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={unreadOnly ? "ai" : "outline"}
              onClick={() => setUnreadOnly((v) => !v)}
              leftIcon={
                unreadOnly ? <Bell className="h-3.5 w-3.5" /> : <BellOff className="h-3.5 w-3.5" />
              }
            >
              {unreadOnly ? "Unread only" : "Showing all"}
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={markAll}
              loading={markingAll}
              disabled={unreadCount === 0}
              leftIcon={<CheckCheck className="h-3.5 w-3.5" />}
            >
              Mark all read
            </Button>
          </div>
        }
      />

      {isLoading ? (
        <ListSkeleton />
      ) : error ? (
        <Card>
          <EmptyState
            icon={<Bell className="h-5 w-5" />}
            title="Could not load alerts"
            description="The API may be unreachable. Try refreshing in a moment."
          />
        </Card>
      ) : alerts.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Bell className="h-5 w-5" />}
            title={unreadOnly ? "No unread alerts" : "No alerts yet"}
            description="You're all caught up. New reputation issues will surface here."
          />
        </Card>
      ) : (
        <StaggerList className="space-y-2.5">
          {alerts.map((a) => {
            const c = severityColor(a.severity);
            const tone = darkSeverityTone(a.severity);
            return (
              <FadeInItem key={String(a.id)}>
                <Card
                  interactive
                  className={cn(
                    "flex items-start gap-3.5 p-4 sm:p-5",
                    !a.is_read && "ring-1 ring-inset ring-ai-indigo/25"
                  )}
                >
                  <span
                    className={cn(
                      "mt-1 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
                      tone
                    )}
                    aria-hidden
                  >
                    <Bell className="h-4.5 w-4.5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-sm font-semibold text-slate-100">
                        {a.title}
                      </p>
                      <span
                        className={cn(
                          "shrink-0 rounded-full px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide",
                          tone
                        )}
                      >
                        {c.label}
                      </span>
                      {!a.is_read ? (
                        <span className="h-2 w-2 shrink-0 rounded-full bg-ai-indigo" aria-label="Unread" />
                      ) : null}
                    </div>
                    <p className="mt-0.5 text-sm text-slate-400">{a.message}</p>
                    <p className="mt-1.5 text-xs text-slate-500">{timeAgo(a.created_at)}</p>
                  </div>
                  {!a.is_read ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      loading={busyId === String(a.id)}
                      onClick={() => markRead(a)}
                      leftIcon={<Check className="h-3.5 w-3.5" />}
                    >
                      Read
                    </Button>
                  ) : null}
                </Card>
              </FadeInItem>
            );
          })}
        </StaggerList>
      )}
    </div>
  );
}

/**
 * Dark-theme severity tone (bg + text) for the alert icon tile and pill.
 * Mirrors severityColor() labels but uses brightened on-dark semantic colors
 * per the dark design spec instead of the light xx-50/xx-700 pastels.
 */
function darkSeverityTone(severity: string): string {
  switch (severity) {
    case "critical":
      return "bg-red-500/15 text-red-300";
    case "high":
      return "bg-orange-500/15 text-orange-300";
    case "medium":
      return "bg-amber-500/15 text-amber-300";
    case "low":
    default:
      return "bg-white/[0.06] text-slate-400";
  }
}

function ListSkeleton() {
  return (
    <div className="space-y-2.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Card key={i} className="flex items-start gap-3.5 p-5">
          <Skeleton className="h-9 w-9 rounded-lg" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-3 w-3/4" />
            <Skeleton className="h-3 w-20" />
          </div>
        </Card>
      ))}
    </div>
  );
}
