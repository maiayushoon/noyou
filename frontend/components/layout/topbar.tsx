"use client";

import { useCallback, useState } from "react";
import { usePathname } from "next/navigation";
import { useSWRConfig } from "swr";
import { Menu, RefreshCw } from "lucide-react";
import { api, type Scan } from "@/lib/api";
import { useToast } from "@/lib/toast";
import { useAuth } from "@/lib/auth";
import { bandColor, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { NAV_ITEMS } from "./nav";

function pageTitle(pathname: string): string {
  const match = NAV_ITEMS.find((item) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href)
  );
  return match?.label ?? "Overview";
}

/** Poll a scan until it reaches a terminal state or times out. */
async function pollScan(
  id: Scan["id"],
  { tries = 30, intervalMs = 2000 }: { tries?: number; intervalMs?: number } = {}
): Promise<Scan> {
  let last: Scan | null = null;
  for (let i = 0; i < tries; i++) {
    const scan = await api.getScan(id);
    last = scan;
    if (scan.status === "completed" || scan.status === "failed") return scan;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  if (last) return last;
  throw new Error("Scan timed out");
}

export function Topbar({ onOpenMenu }: { onOpenMenu: () => void }) {
  const pathname = usePathname();
  const toast = useToast();
  const { user, refresh } = useAuth();
  const { mutate } = useSWRConfig();
  const [scanning, setScanning] = useState(false);

  const runScan = useCallback(async () => {
    setScanning(true);
    try {
      const started = await api.startScan();
      toast.info("Scan started", "Searching connectors for new mentions…");
      const result = await pollScan(started.id);
      if (result.status === "completed") {
        toast.success(
          "Scan complete",
          `${result.new_mentions ?? 0} new mention${
            result.new_mentions === 1 ? "" : "s"
          } found.`
        );
      } else {
        toast.error("Scan failed", "Please try again in a moment.");
      }
      // Refresh dependent data + the current user's score.
      await Promise.all([
        mutate("dashboard"),
        mutate("reports"),
        mutate((key) => typeof key === "string" && key.startsWith("mentions"), undefined, { revalidate: true }),
        refresh(),
      ]);
    } catch (err) {
      toast.error(
        "Could not run scan",
        err instanceof Error ? err.message : undefined
      );
    } finally {
      setScanning(false);
    }
  }, [toast, mutate, refresh]);

  const band = user ? bandColor(scoreBand(user.reputation_score)) : null;

  return (
    <header className="glass sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-hairline px-4 sm:px-6">
      <button
        type="button"
        onClick={onOpenMenu}
        aria-label="Open navigation"
        className="-ml-1 inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 lg:hidden"
      >
        <Menu className="h-5 w-5" aria-hidden />
      </button>

      <h1 className="truncate text-base font-semibold tracking-tight text-slate-900">
        {pageTitle(pathname)}
      </h1>

      <div className="ml-auto flex items-center gap-2.5 sm:gap-3">
        {user ? (
          <div
            className={cn(
              "hidden items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset sm:inline-flex",
              band?.bg,
              band?.text,
              band?.ring
            )}
            title="Your current reputation score"
          >
            <span className={cn("h-1.5 w-1.5 rounded-full", band?.dot)} aria-hidden />
            Score {user.reputation_score}
          </div>
        ) : null}

        <Button
          variant="ai"
          size="sm"
          onClick={runScan}
          loading={scanning}
          leftIcon={!scanning ? <RefreshCw className="h-4 w-4" /> : undefined}
        >
          {scanning ? "Scanning…" : "Run scan"}
        </Button>
      </div>
    </header>
  );
}

function scoreBand(score: number): "low" | "medium" | "high" | "critical" {
  if (score >= 75) return "high";
  if (score >= 50) return "medium";
  if (score >= 25) return "low";
  return "critical";
}
