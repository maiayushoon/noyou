"use client";

import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Card } from "./card";
import { Skeleton } from "./skeleton";

export interface StatProps {
  label: string;
  value: React.ReactNode;
  icon?: React.ReactNode;
  hint?: string;
  /** Tailwind classes for the icon tile (bg + text). */
  accentClassName?: string;
  loading?: boolean;
  className?: string;
  index?: number;
}

export function Stat({
  label,
  value,
  icon,
  hint,
  accentClassName = "bg-slate-100 text-slate-600",
  loading = false,
  className,
  index = 0,
}: StatProps) {
  const reduce = useReducedMotion();

  if (loading) {
    return (
      <Card className={cn("p-5", className)}>
        <div className="flex items-center justify-between">
          <Skeleton className="h-3.5 w-24" />
          <Skeleton className="h-9 w-9 rounded-lg" />
        </div>
        <Skeleton className="mt-4 h-8 w-20" />
        <Skeleton className="mt-2 h-3 w-28" />
      </Card>
    );
  }

  return (
    <motion.div
      initial={reduce ? false : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, delay: index * 0.05, ease: "easeOut" }}
    >
      <Card interactive className={cn("p-5", className)}>
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-slate-500">{label}</p>
          {icon ? (
            <span
              className={cn(
                "inline-flex h-9 w-9 items-center justify-center rounded-lg",
                accentClassName
              )}
              aria-hidden
            >
              {icon}
            </span>
          ) : null}
        </div>
        <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
          {value}
        </p>
        {hint ? <p className="mt-1 text-sm text-slate-500">{hint}</p> : null}
      </Card>
    </motion.div>
  );
}
