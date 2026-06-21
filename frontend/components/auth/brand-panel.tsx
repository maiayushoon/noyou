"use client";

import { useEffect, useRef, useState } from "react";
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
  type MotionValue,
} from "framer-motion";
import { ShieldCheck, Sparkles, TrendingUp, Eye } from "lucide-react";

/**
 * Animated left brand panel for the auth split-screen.
 * Self-contained client component: the signature floating, mouse-tilting
 * 3D reputation ring, a drifting cluster of user avatars, blurred gradient
 * orbs, and floating glass stat chips. Honors prefers-reduced-motion.
 */
export function BrandPanel() {
  const reduce = useReducedMotion();
  const containerRef = useRef<HTMLDivElement>(null);

  // Normalized pointer position in [-1, 1], smoothed via springs.
  const px = useMotionValue(0);
  const py = useMotionValue(0);
  const springConfig = { stiffness: 120, damping: 18, mass: 0.4 };
  const sx = useSpring(px, springConfig);
  const sy = useSpring(py, springConfig);

  useEffect(() => {
    if (reduce) return;
    const el = containerRef.current;
    if (!el) return;

    function onMove(e: PointerEvent) {
      const rect = el!.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / rect.width; // 0..1
      const ny = (e.clientY - rect.top) / rect.height; // 0..1
      px.set(Math.max(-1, Math.min(1, nx * 2 - 1)));
      py.set(Math.max(-1, Math.min(1, ny * 2 - 1)));
    }
    function onLeave() {
      px.set(0);
      py.set(0);
    }

    el.addEventListener("pointermove", onMove);
    el.addEventListener("pointerleave", onLeave);
    return () => {
      el.removeEventListener("pointermove", onMove);
      el.removeEventListener("pointerleave", onLeave);
    };
  }, [reduce, px, py]);

  return (
    <div
      ref={containerRef}
      className="relative hidden flex-col justify-between overflow-hidden bg-sidebar p-12 lg:flex"
    >
      {/* Blurred drifting gradient orbs (depth backdrop) */}
      <Orbs reduce={!!reduce} />

      {/* Subtle dot grid for premium depth */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.18]"
        style={{
          backgroundImage:
            "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.35) 1px, transparent 0)",
          backgroundSize: "28px 28px",
          maskImage:
            "radial-gradient(ellipse 70% 60% at 50% 45%, black 30%, transparent 80%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 70% 60% at 50% 45%, black 30%, transparent 80%)",
        }}
        aria-hidden
      />

      {/* Logo (top-left) */}
      <motion.div
        className="relative z-10 flex items-center gap-2.5"
        initial={reduce ? false : { opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-ai-gradient shadow-ai">
          <ShieldCheck className="h-5 w-5 text-white" aria-hidden />
        </span>
        <span className="text-lg font-semibold tracking-tight text-white">
          NoYou
        </span>
      </motion.div>

      {/* Center living scene */}
      <div className="relative z-10 flex flex-1 flex-col justify-center py-10">
        <Hero reduce={!!reduce} sx={sx} sy={sy} />

        <motion.div
          className="mt-10 max-w-md"
          initial={reduce ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.25, ease: "easeOut" }}
        >
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-slate-200 ring-1 ring-inset ring-white/10">
            <Sparkles className="h-3.5 w-3.5" aria-hidden />
            AI reputation intelligence
          </span>
          <h1 className="mt-5 text-3xl font-semibold leading-tight tracking-tight text-white">
            Know what the internet —{" "}
            <span className="text-gradient-ai">and AI</span> — says about you.
          </h1>
          <p className="mt-4 text-[0.95rem] leading-relaxed text-slate-400">
            NoYou monitors mentions across the web, scores your reputation in
            real time, and recommends exactly what to clean up next.
          </p>

          <TrustCluster reduce={!!reduce} />
        </motion.div>
      </div>

      {/* Copyright (bottom) */}
      <p className="relative z-10 text-xs text-slate-500">
        © {new Date().getFullYear()} NoYou. Your reputation, protected.
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Gradient orbs                                                        */
/* ------------------------------------------------------------------ */

function Orbs({ reduce }: { reduce: boolean }) {
  return (
    <>
      <motion.div
        className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-ai-gradient opacity-30 blur-3xl"
        aria-hidden
        animate={
          reduce
            ? undefined
            : { x: [0, 18, -8, 0], y: [0, -14, 10, 0], scale: [1, 1.06, 0.98, 1] }
        }
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="pointer-events-none absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-ai-gradient opacity-20 blur-3xl"
        aria-hidden
        animate={
          reduce
            ? undefined
            : { x: [0, -14, 12, 0], y: [0, 12, -10, 0], scale: [1, 1.05, 0.97, 1] }
        }
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="pointer-events-none absolute left-1/2 top-1/3 h-72 w-72 -translate-x-1/2 rounded-full bg-ai-cyan opacity-10 blur-3xl"
        aria-hidden
        animate={reduce ? undefined : { scale: [1, 1.12, 1], opacity: [0.08, 0.14, 0.08] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />
    </>
  );
}

/* ------------------------------------------------------------------ */
/* Hero — floating, mouse-tilting 3D reputation ring                   */
/* ------------------------------------------------------------------ */

function Hero({
  reduce,
  sx,
  sy,
}: {
  reduce: boolean;
  sx: MotionValue<number>;
  sy: MotionValue<number>;
}) {
  // Mouse-parallax tilt. Map pointer (-1..1) to gentle rotation degrees.
  const rotateY = useTransform(sx, [-1, 1], [14, -14]);
  const rotateX = useTransform(sy, [-1, 1], [-12, 12]);
  // Layered depth: chips and ring shift slightly opposite for parallax.
  const ringX = useTransform(sx, [-1, 1], [-10, 10]);
  const ringY = useTransform(sy, [-1, 1], [-10, 10]);
  const chipFarX = useTransform(sx, [-1, 1], [22, -22]);
  const chipFarY = useTransform(sy, [-1, 1], [16, -16]);
  const chipNearX = useTransform(sx, [-1, 1], [-26, 26]);
  const chipNearY = useTransform(sy, [-1, 1], [-18, 18]);

  return (
    <div
      className="relative mx-auto flex h-[300px] w-full max-w-md items-center justify-center"
      style={{ perspective: "1200px" }}
    >
      <motion.div
        className="relative"
        style={
          reduce
            ? undefined
            : { rotateX, rotateY, transformStyle: "preserve-3d" }
        }
        initial={reduce ? false : { opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        {/* Gentle continuous float wrapper */}
        <motion.div
          animate={reduce ? undefined : { y: [0, -12, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          style={{ transformStyle: "preserve-3d" }}
        >
          {/* Glow behind ring */}
          <div
            className="pointer-events-none absolute left-1/2 top-1/2 h-56 w-56 -translate-x-1/2 -translate-y-1/2 rounded-full bg-ai-gradient opacity-40 blur-2xl"
            aria-hidden
            style={{ transform: "translate(-50%, -50%) translateZ(-60px)" }}
          />

          {/* The reputation ring */}
          <motion.div
            style={
              reduce ? undefined : { x: ringX, y: ringY, transformStyle: "preserve-3d" }
            }
          >
            <ReputationRing reduce={reduce} />
          </motion.div>

          {/* Floating glass stat chips, layered in 3D */}
          <motion.div
            className="absolute -left-10 -top-2"
            style={
              reduce
                ? undefined
                : { x: chipFarX, y: chipFarY, z: 70, transformStyle: "preserve-3d" }
            }
          >
            <FloatChip
              reduce={reduce}
              delay={0.4}
              icon={<TrendingUp className="h-4 w-4 text-emerald-300" aria-hidden />}
              label="Reputation"
              value="92"
              tone="up"
            />
          </motion.div>

          <motion.div
            className="absolute -right-8 bottom-2"
            style={
              reduce
                ? undefined
                : { x: chipNearX, y: chipNearY, z: 90, transformStyle: "preserve-3d" }
            }
          >
            <FloatChip
              reduce={reduce}
              delay={0.55}
              icon={<Eye className="h-4 w-4 text-ai-cyan" aria-hidden />}
              label="Mentions tracked"
              value="1,284"
            />
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
}

function ReputationRing({ reduce }: { reduce: boolean }) {
  const SIZE = 210;
  const R = 86;
  const C = 2 * Math.PI * R;
  const score = 92;
  const dash = (score / 100) * C;

  return (
    <div
      className="relative grid place-items-center"
      style={{ width: SIZE, height: SIZE }}
    >
      {/* Slowly rotating outer gradient ring */}
      <motion.svg
        width={SIZE}
        height={SIZE}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="absolute inset-0"
        role="img"
        aria-label="Reputation score 92 out of 100"
        animate={reduce ? undefined : { rotate: 360 }}
        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
      >
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#C8A24C" />
            <stop offset="50%" stopColor="#D9B86A" />
            <stop offset="100%" stopColor="#F0E3BE" />
          </linearGradient>
          <filter id="ringGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Track */}
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={R}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={12}
        />
        {/* Progress arc */}
        <motion.circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={R}
          fill="none"
          stroke="url(#ringGrad)"
          strokeWidth={12}
          strokeLinecap="round"
          filter="url(#ringGlow)"
          strokeDasharray={C}
          transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
          initial={reduce ? { strokeDashoffset: C - dash } : { strokeDashoffset: C }}
          animate={{ strokeDashoffset: C - dash }}
          transition={{ duration: 1.6, delay: 0.3, ease: "easeOut" }}
        />
        {/* Tick marks */}
        {Array.from({ length: 60 }).map((_, i) => {
          const a = (i / 60) * 2 * Math.PI;
          const inner = R + 14;
          const outer = R + (i % 5 === 0 ? 22 : 18);
          const cx = SIZE / 2;
          const cy = SIZE / 2;
          // Round so server and client render byte-identical strings (no hydration mismatch).
          const r3 = (n: number) => Number(n.toFixed(3));
          return (
            <line
              key={i}
              x1={r3(cx + inner * Math.cos(a))}
              y1={r3(cy + inner * Math.sin(a))}
              x2={r3(cx + outer * Math.cos(a))}
              y2={r3(cy + outer * Math.sin(a))}
              stroke="rgba(255,255,255,0.12)"
              strokeWidth={i % 5 === 0 ? 1.5 : 0.75}
            />
          );
        })}
      </motion.svg>

      {/* Glassy inner disc (counter-rotates visually static) */}
      <div
        className="relative grid h-[150px] w-[150px] place-items-center rounded-full border border-white/10 bg-white/[0.04] backdrop-blur-sm"
        style={{
          boxShadow:
            "inset 0 1px 0 rgba(255,255,255,0.18), 0 20px 50px rgba(200,162,76,0.35)",
        }}
      >
        <div className="flex flex-col items-center">
          <span className="inline-flex items-center gap-1 text-[0.7rem] font-medium uppercase tracking-wider text-slate-400">
            <ShieldCheck className="h-3.5 w-3.5 text-ai-cyan" aria-hidden />
            Reputation
          </span>
          <div className="mt-1 flex items-end gap-1">
            <span className="bg-gradient-to-br from-white to-slate-300 bg-clip-text text-5xl font-bold leading-none tracking-tight text-transparent">
              {score}
            </span>
            <span className="mb-1 text-sm font-medium text-slate-400">/100</span>
          </div>
          <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-emerald-400/10 px-2 py-0.5 text-[0.7rem] font-medium text-emerald-300 ring-1 ring-inset ring-emerald-400/20">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" aria-hidden />
            Strong &amp; trending up
          </span>
        </div>
      </div>
    </div>
  );
}

function FloatChip({
  reduce,
  delay,
  icon,
  label,
  value,
  tone,
}: {
  reduce: boolean;
  delay: number;
  icon: React.ReactNode;
  label: string;
  value: string;
  tone?: "up";
}) {
  return (
    <motion.div
      className="flex items-center gap-2.5 rounded-xl border border-white/10 bg-white/[0.07] px-3 py-2 shadow-xl backdrop-blur-md"
      style={{
        boxShadow:
          "0 10px 30px rgba(2,6,23,0.45), inset 0 1px 0 rgba(255,255,255,0.12)",
      }}
      initial={reduce ? false : { opacity: 0, scale: 0.85, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
    >
      <motion.span
        className="grid h-8 w-8 place-items-center rounded-lg bg-white/10"
        animate={reduce ? undefined : { y: [0, -3, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay }}
      >
        {icon}
      </motion.span>
      <div className="leading-tight">
        <div className="flex items-center gap-1 text-base font-semibold text-white">
          {value}
          {tone === "up" ? (
            <TrendingUp className="h-3.5 w-3.5 text-emerald-300" aria-hidden />
          ) : null}
        </div>
        <div className="text-[0.7rem] text-slate-400">{label}</div>
      </div>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/* Trust cluster — drifting avatar stack                               */
/* ------------------------------------------------------------------ */

const AVATARS = [12, 26, 33, 47, 58] as const;

function TrustCluster({ reduce }: { reduce: boolean }) {
  return (
    <motion.div
      className="mt-7 flex items-center gap-4"
      initial={reduce ? false : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.45, ease: "easeOut" }}
    >
      <motion.div
        className="flex -space-x-3"
        animate={reduce ? undefined : { y: [0, -4, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
      >
        {AVATARS.map((n, i) => (
          <Avatar key={n} n={n} index={i} reduce={reduce} />
        ))}
        <span
          className="grid h-10 w-10 place-items-center rounded-full bg-white/10 text-[0.7rem] font-semibold text-slate-200 ring-2 ring-sidebar"
          aria-hidden
        >
          12k+
        </span>
      </motion.div>
      <p className="text-xs leading-snug text-slate-400">
        <span className="font-semibold text-slate-200">12,000+ people</span>
        <br />
        protect their reputation with NoYou.
      </p>
    </motion.div>
  );
}

function Avatar({
  n,
  index,
  reduce,
}: {
  n: number;
  index: number;
  reduce: boolean;
}) {
  const [failed, setFailed] = useState(false);
  // Per-avatar gradient fallback hues for variety.
  const fallbackGradients = [
    "from-[#C8A24C] to-[#E8D7A8]",
    "from-[#E8D7A8] to-[#C8A24C]",
    "from-[#F0E3BE] to-[#D9B86A]",
    "from-[#A9853A] to-[#E8D7A8]",
    "from-[#86692E] to-[#C8A24C]",
  ] as const;
  const grad = fallbackGradients[index % fallbackGradients.length]!;

  return (
    <motion.div
      className="relative"
      initial={reduce ? false : { opacity: 0, scale: 0.6 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.5 + index * 0.06, ease: "easeOut" }}
    >
      {failed ? (
        <span
          className={`grid h-10 w-10 place-items-center rounded-full bg-gradient-to-br ${grad} text-xs font-semibold text-white ring-2 ring-sidebar`}
          aria-hidden
        >
          {String.fromCharCode(65 + ((n * 7) % 26))}
        </span>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={`https://i.pravatar.cc/96?img=${n}`}
          alt=""
          width={40}
          height={40}
          loading="lazy"
          onError={() => setFailed(true)}
          className="h-10 w-10 rounded-full object-cover ring-2 ring-sidebar"
        />
      )}
    </motion.div>
  );
}
