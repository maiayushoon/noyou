"use client";

import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
} from "framer-motion";
import { ShieldCheck, TrendingUp, Sparkles, Eye } from "lucide-react";
import type { PointerEvent } from "react";

const SCORE = 92;
const BAND = "Excellent";

/**
 * The signature hero centerpiece: a floating, mouse-tilting 3D reputation ring.
 *
 * Built entirely from SVG + CSS layers (no WebGL):
 *  - an SVG gradient progress ring rendering the reputation score,
 *  - glassy translucent cards layered at different depths (preserve-3d),
 *  - glowing blurred gradient orbs behind it,
 *  - a gentle continuous drift, and a mouse-parallax tilt (rotateX / rotateY).
 *
 * Fully reduced-motion safe: when the user prefers reduced motion, the tilt and
 * drift are disabled and the ring renders statically.
 */
export default function ReputationOrb() {
  const reduceMotion = useReducedMotion();

  // Normalized pointer position (-0.5 .. 0.5) drives the tilt.
  const px = useMotionValue(0);
  const py = useMotionValue(0);

  const springConfig = { stiffness: 120, damping: 18, mass: 0.6 };
  const rotateX = useSpring(useTransform(py, [-0.5, 0.5], [8, -8]), springConfig);
  const rotateY = useSpring(useTransform(px, [-0.5, 0.5], [-12, 12]), springConfig);

  // Layered parallax: closer layers shift more than the ring. Hooks are called at
  // the top level (not via a helper) to satisfy the Rules of Hooks.
  const shiftFront = useSpring(useTransform(px, [-0.5, 0.5], [-18, 18]), springConfig);
  const shiftMid = useSpring(useTransform(px, [-0.5, 0.5], [-10, 10]), springConfig);
  const shiftFrontY = useSpring(
    useTransform(py, [-0.5, 0.5], [-12, 12]),
    springConfig,
  );

  function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
    if (reduceMotion) return;
    const rect = event.currentTarget.getBoundingClientRect();
    px.set((event.clientX - rect.left) / rect.width - 0.5);
    py.set((event.clientY - rect.top) / rect.height - 0.5);
  }

  function resetTilt() {
    px.set(0);
    py.set(0);
  }

  // Ring geometry.
  const radius = 92;
  const circumference = 2 * Math.PI * radius;
  const dash = (SCORE / 100) * circumference;

  return (
    <div
      className="relative mx-auto flex aspect-square w-full max-w-[460px] items-center justify-center"
      style={{ perspective: "1200px" }}
      onPointerMove={handlePointerMove}
      onPointerLeave={resetTilt}
      role="img"
      aria-label={`Reputation score ${SCORE} out of 100, rated ${BAND}.`}
    >
      {/* Glowing blurred gradient orbs behind the centerpiece. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-6 top-6 h-56 w-56 rounded-full bg-indigo-500/40 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-4 bottom-2 h-52 w-52 rounded-full bg-cyan-400/35 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-500/35 blur-3xl"
      />

      <motion.div
        className="relative h-full w-full"
        style={{
          transformStyle: "preserve-3d",
          rotateX: reduceMotion ? 0 : rotateX,
          rotateY: reduceMotion ? 0 : rotateY,
        }}
        animate={
          reduceMotion
            ? undefined
            : { y: [0, -12, 0] }
        }
        transition={
          reduceMotion
            ? undefined
            : { duration: 7, repeat: Infinity, ease: "easeInOut" }
        }
      >
        {/* Back glass panel for depth. */}
        <div
          aria-hidden="true"
          className="absolute inset-6 rounded-[2rem] border border-white/10 bg-white/[0.04] backdrop-blur-md"
          style={{ transform: "translateZ(-40px)" }}
        />

        {/* The reputation ring (SVG). */}
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{ transform: "translateZ(20px)" }}
        >
          <svg
            viewBox="0 0 240 240"
            className="h-[78%] w-[78%] drop-shadow-[0_18px_40px_rgba(99,102,241,0.35)]"
            aria-hidden="true"
          >
            <defs>
              <linearGradient id="orb-ring" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="50%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#22d3ee" />
              </linearGradient>
              <radialGradient id="orb-core" cx="50%" cy="42%" r="65%">
                <stop offset="0%" stopColor="#1a1a2e" />
                <stop offset="70%" stopColor="#101019" />
                <stop offset="100%" stopColor="#0b0b14" />
              </radialGradient>
            </defs>

            {/* Glassy core disc. */}
            <circle cx="120" cy="120" r="80" fill="url(#orb-core)" />
            <circle
              cx="120"
              cy="120"
              r="80"
              fill="none"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="1"
            />

            {/* Track. */}
            <circle
              cx="120"
              cy="120"
              r={radius}
              fill="none"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="14"
            />

            {/* Animated progress arc. */}
            <motion.circle
              cx="120"
              cy="120"
              r={radius}
              fill="none"
              stroke="url(#orb-ring)"
              strokeWidth="14"
              strokeLinecap="round"
              strokeDasharray={circumference}
              transform="rotate(-90 120 120)"
              initial={
                reduceMotion
                  ? { strokeDashoffset: circumference - dash }
                  : { strokeDashoffset: circumference }
              }
              whileInView={{ strokeDashoffset: circumference - dash }}
              viewport={{ once: true }}
              transition={
                reduceMotion
                  ? { duration: 0 }
                  : { duration: 1.6, ease: [0.22, 1, 0.36, 1], delay: 0.2 }
              }
            />
          </svg>
        </div>

        {/* Score readout, floating slightly above the ring. */}
        <motion.div
          className="absolute inset-0 flex flex-col items-center justify-center text-center"
          style={{
            transform: "translateZ(56px)",
            x: reduceMotion ? 0 : shiftMid,
          }}
        >
          <span className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">
            Reputation
          </span>
          <span className="bg-gradient-to-br from-indigo-400 via-violet-400 to-cyan-300 bg-clip-text text-6xl font-black leading-none text-transparent sm:text-7xl">
            {SCORE}
          </span>
          <span className="mt-1 inline-flex items-center gap-1 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-bold text-emerald-300 ring-1 ring-emerald-500/30">
            <TrendingUp className="h-3.5 w-3.5" aria-hidden="true" />
            {BAND}
          </span>
        </motion.div>

        {/* Floating glass chip: shield (top-left). */}
        <motion.div
          className="absolute left-0 top-8 flex items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.06] px-3 py-2 shadow-ai backdrop-blur-md"
          style={{
            transform: "translateZ(80px)",
            x: reduceMotion ? 0 : shiftFront,
            y: reduceMotion ? 0 : shiftFrontY,
          }}
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-ai-gradient text-white">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="text-left">
            <span className="block text-[11px] font-semibold leading-tight text-slate-100">
              0 high-risk
            </span>
            <span className="block text-[10px] leading-tight text-slate-400">
              mentions today
            </span>
          </span>
        </motion.div>

        {/* Floating glass chip: AI visibility (bottom-right). */}
        <motion.div
          className="absolute bottom-10 right-0 flex items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.06] px-3 py-2 shadow-ai backdrop-blur-md"
          style={{
            transform: "translateZ(72px)",
            x: reduceMotion ? 0 : shiftFront,
            y: reduceMotion ? 0 : shiftFrontY,
          }}
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-500 text-white">
            <Eye className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="text-left">
            <span className="block text-[11px] font-semibold leading-tight text-slate-100">
              4 AI engines
            </span>
            <span className="block text-[10px] leading-tight text-slate-400">
              describe you well
            </span>
          </span>
        </motion.div>

        {/* Small sparkle accent. */}
        <motion.div
          className="absolute right-10 top-2 text-violet-400"
          style={{ transform: "translateZ(90px)" }}
          animate={reduceMotion ? undefined : { rotate: [0, 12, 0], scale: [1, 1.12, 1] }}
          transition={
            reduceMotion
              ? undefined
              : { duration: 5, repeat: Infinity, ease: "easeInOut" }
          }
          aria-hidden="true"
        >
          <Sparkles className="h-6 w-6" />
        </motion.div>
      </motion.div>
    </div>
  );
}
