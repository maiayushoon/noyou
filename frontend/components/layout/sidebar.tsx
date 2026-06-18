"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { LogOut, ShieldCheck } from "lucide-react";
import { NAV_ITEMS } from "./nav";
import { useAuth } from "@/lib/auth";
import { cn, humanize } from "@/lib/utils";

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

export function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex h-full flex-col bg-sidebar text-slate-300">
      {/* Brand */}
      <div className="flex h-16 items-center gap-2.5 px-5">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-ai-gradient shadow-ai">
          <ShieldCheck className="h-4.5 w-4.5 text-white" aria-hidden />
        </span>
        <span className="text-[0.95rem] font-semibold tracking-tight text-white">
          NoYou
        </span>
      </div>

      {/* Nav */}
      <nav className="sidebar-scroll flex-1 space-y-1 overflow-y-auto px-3 py-3">
        {NAV_ITEMS.map((item) => {
          const active = isActive(pathname, item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              aria-current={active ? "page" : undefined}
              className={cn(
                "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "text-white"
                  : "text-slate-400 hover:bg-sidebar-hover hover:text-slate-100"
              )}
            >
              {active ? (
                <motion.span
                  layoutId="sidebar-active"
                  className="absolute inset-0 -z-0 rounded-lg bg-ai-gradient opacity-95 shadow-ai"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                />
              ) : null}
              <Icon className="relative z-10 h-4.5 w-4.5 shrink-0" aria-hidden />
              <span className="relative z-10 truncate">{item.label}</span>
              {item.ai ? (
                <span
                  className={cn(
                    "relative z-10 ml-auto rounded px-1.5 py-0.5 text-[10px] font-semibold tracking-wide",
                    active
                      ? "bg-white/20 text-white"
                      : "bg-white/5 text-slate-400 group-hover:text-slate-200"
                  )}
                >
                  AI
                </span>
              ) : null}
            </Link>
          );
        })}
      </nav>

      {/* User + plan + sign out */}
      <div className="border-t border-white/10 p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sidebar-hover text-xs font-semibold text-slate-200">
            {initials(user?.full_name || user?.email)}
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-100">
              {user?.full_name || user?.email || "—"}
            </p>
            <p className="truncate text-xs text-slate-500">
              {user ? humanize(user.plan) : "Free"} plan
            </p>
          </div>
          <button
            type="button"
            onClick={logout}
            aria-label="Sign out"
            className="shrink-0 rounded-md p-1.5 text-slate-400 transition-colors hover:bg-sidebar-hover hover:text-white"
          >
            <LogOut className="h-4 w-4" aria-hidden />
          </button>
        </div>
      </div>
    </div>
  );
}

function initials(name?: string | null): string {
  if (!name) return "N";
  const parts = name.split(/[\s@.]+/).filter(Boolean);
  if (parts.length === 0) return "N";
  if (parts.length === 1) return (parts[0]!.slice(0, 2)).toUpperCase();
  return (parts[0]![0]! + parts[1]![0]!).toUpperCase();
}

/** Fixed desktop sidebar. */
export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 lg:block">
      <div className="fixed inset-y-0 left-0 w-64">
        <SidebarContent />
      </div>
    </aside>
  );
}
