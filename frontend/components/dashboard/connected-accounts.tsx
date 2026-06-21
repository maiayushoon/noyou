"use client";

import { useState } from "react";
import Link from "next/link";
import useSWR from "swr";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Plus, Users } from "lucide-react";
import { api, type Connection } from "@/lib/api";
import { cn, humanize } from "@/lib/utils";

/* -------------------------------------------------------------------------- */
/*  ConnectedAccounts — an overlapping avatar stack for linked accounts.      */
/*                                                                            */
/*  Pulls connections via SWR (same "connections" key the page already        */
/*  warms, so this is effectively free). Renders each connected account's     */
/*  real avatar_url as an overlapping, softly-floating avatar with a          */
/*  gradient-initial fallback on error and a small provider badge. With no    */
/*  connections, shows a subtle "Connect an account" link instead.           */
/* -------------------------------------------------------------------------- */

const MAX_AVATARS = 5;

export function ConnectedAccounts() {
  const { data, isLoading } = useSWR<Connection[]>(
    "connections",
    () => api.listConnections(),
    { shouldRetryOnError: false }
  );
  const reduce = useReducedMotion();

  // While the (cheap, cached) fetch is in flight, render nothing rather than
  // a layout-shifting placeholder — the rest of the hero is unaffected.
  if (isLoading) return null;

  const connected = (data ?? []).filter((c) => c.status === "connected");

  if (connected.length === 0) {
    return (
      <Link
        href="/connections"
        className="group inline-flex items-center gap-2 text-xs font-medium text-slate-500 transition-colors hover:text-ai-indigo"
      >
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-dashed border-slate-300 text-slate-400 transition-colors group-hover:border-ai-indigo group-hover:text-ai-indigo">
          <Plus className="h-3.5 w-3.5" aria-hidden />
        </span>
        Connect an account
        <ArrowRight
          className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5"
          aria-hidden
        />
      </Link>
    );
  }

  const shown = connected.slice(0, MAX_AVATARS);
  const overflow = connected.length - shown.length;

  return (
    <div className="flex items-center gap-3">
      <div className="flex -space-x-2.5" aria-hidden>
        {shown.map((c, i) => (
          <motion.div
            key={c.id}
            initial={reduce ? false : { opacity: 0, scale: 0.6 }}
            animate={
              reduce
                ? { opacity: 1, scale: 1 }
                : { opacity: 1, scale: 1, y: [0, -3, 0] }
            }
            transition={{
              opacity: { duration: 0.3, delay: i * 0.06 },
              scale: { duration: 0.3, delay: i * 0.06, ease: "easeOut" },
              y: reduce
                ? { duration: 0 }
                : {
                    duration: 3.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.25,
                  },
            }}
            style={{ zIndex: shown.length - i }}
            className="relative"
          >
            <Avatar connection={c} index={i} />
          </motion.div>
        ))}
        {overflow > 0 ? (
          <span
            className="relative inline-flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-[11px] font-semibold text-slate-500 ring-2 ring-white"
            style={{ zIndex: 0 }}
          >
            +{overflow}
          </span>
        ) : null}
      </div>

      <Link
        href="/connections"
        className="group inline-flex items-center gap-1 text-xs text-slate-500 transition-colors hover:text-ai-indigo"
      >
        <Users className="h-3.5 w-3.5 text-slate-400" aria-hidden />
        <span>
          Pulling from your{" "}
          <span className="font-semibold text-slate-700">
            {connected.length}
          </span>{" "}
          connected account{connected.length === 1 ? "" : "s"}
        </span>
        <ArrowRight
          className="h-3 w-3 opacity-0 transition-all group-hover:translate-x-0.5 group-hover:opacity-100"
          aria-hidden
        />
      </Link>
    </div>
  );
}

/* --------------------------------- Avatar --------------------------------- */

const FALLBACK_GRADIENTS = [
  "from-[#C8A24C] to-[#E8D7A8]",
  "from-[#E8D7A8] to-[#F0E3BE]",
  "from-[#F0E3BE] to-[#C8A24C]",
  "from-[#A9853A] to-[#C8A24C]",
  "from-[#86692E] to-[#E8D7A8]",
];

function Avatar({ connection, index }: { connection: Connection; index: number }) {
  const [errored, setErrored] = useState(false);

  const name =
    connection.display_name || connection.external_handle || connection.provider;
  const initial = (name?.trim()?.[0] ?? "?").toUpperCase();
  const gradient = FALLBACK_GRADIENTS[index % FALLBACK_GRADIENTS.length];
  const title = `${name} · ${humanize(connection.provider)}`;

  const showImage = connection.avatar_url && !errored;

  return (
    <span className="relative block" title={title}>
      {showImage ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={connection.avatar_url as string}
          alt={title}
          width={36}
          height={36}
          referrerPolicy="no-referrer"
          onError={() => setErrored(true)}
          className="h-9 w-9 rounded-full bg-slate-100 object-cover ring-2 ring-white"
        />
      ) : (
        <span
          className={cn(
            "flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br text-xs font-semibold text-white ring-2 ring-white",
            gradient
          )}
          aria-hidden
        >
          {initial}
        </span>
      )}
    </span>
  );
}
