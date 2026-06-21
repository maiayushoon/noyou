"use client";

import { useEffect, useId, useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { clamp } from "@/lib/utils";

export interface ScoreRingProps {
  /** Score 0-100. */
  score: number;
  size?: number;
  strokeWidth?: number;
  /** Caption rendered under the number (e.g. band label). */
  label?: string;
  className?: string;
}

/**
 * Signature reputation ring: an SVG track + an AI-gradient progress stroke
 * that sweeps in on mount, with the number counting up in the center.
 * Honors reduced-motion.
 */
export function ScoreRing({
  score,
  size = 180,
  strokeWidth = 14,
  label,
  className,
}: ScoreRingProps) {
  const reduce = useReducedMotion();
  const gradientId = useId();
  const value = clamp(Math.round(score), 0, 100);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - value / 100);

  const [display, setDisplay] = useState(reduce ? value : 0);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (reduce) {
      setDisplay(value);
      return;
    }
    const duration = 900;
    const start = performance.now();
    const from = 0;

    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(from + (value - from) * eased));
      if (t < 1) rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [value, reduce]);

  return (
    <div
      className={className}
      style={{ width: size, height: size, position: "relative" }}
      role="img"
      aria-label={`Reputation score ${value} out of 100${label ? `, ${label}` : ""}`}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#C8A24C" />
            <stop offset="50%" stopColor="#D9B86A" />
            <stop offset="100%" stopColor="#F0E3BE" />
          </linearGradient>
        </defs>
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={strokeWidth}
        />
        {/* Progress */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: reduce ? offset : circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={
            reduce
              ? { duration: 0 }
              : { duration: 0.9, ease: [0.22, 1, 0.36, 1] }
          }
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-semibold tracking-tight tabular-nums text-white">
          {display}
        </span>
        {label ? (
          <span className="mt-0.5 text-xs font-medium uppercase tracking-wide text-slate-400">
            {label}
          </span>
        ) : null}
      </div>
    </div>
  );
}
