"use client";

import { useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ScoreRing } from "@/components/ui";

/* -------------------------------------------------------------------------- */
/*  HeroOrb — a floating, mouse-tilting 3D wrapper around the ScoreRing.       */
/*                                                                            */
/*  Purely additive: the existing <ScoreRing> renders untouched in the        */
/*  center. We layer a soft ai-gradient glow/halo behind it, a gentle         */
/*  continuous float, and a CSS-perspective tilt that follows the pointer     */
/*  (small degrees). Everything is disabled under prefers-reduced-motion.     */
/* -------------------------------------------------------------------------- */

const MAX_TILT = 10; // degrees

export function HeroOrb({
  score,
  label,
  size = 180,
}: {
  score: number;
  label?: string;
  size?: number;
}) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  function handleMove(e: React.MouseEvent<HTMLDivElement>) {
    if (reduce) return;
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    // Pointer position normalized to [-0.5, 0.5] within the element.
    const px = (e.clientX - rect.left) / rect.width - 0.5;
    const py = (e.clientY - rect.top) / rect.height - 0.5;
    setTilt({ x: -py * MAX_TILT * 2, y: px * MAX_TILT * 2 });
  }

  function handleLeave() {
    setTilt({ x: 0, y: 0 });
  }

  return (
    <div
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      className="relative flex items-center justify-center"
      style={{ perspective: 900 }}
    >
      {/* Soft ai-gradient glow / halo behind the ring */}
      <motion.div
        aria-hidden
        className="pointer-events-none absolute rounded-full bg-ai-gradient opacity-25 blur-2xl"
        style={{ width: size * 0.92, height: size * 0.92 }}
        animate={
          reduce
            ? undefined
            : { scale: [1, 1.08, 1], opacity: [0.22, 0.32, 0.22] }
        }
        transition={
          reduce
            ? undefined
            : { duration: 6, repeat: Infinity, ease: "easeInOut" }
        }
      />
      {/* A second, tighter cyan-tinted bloom for depth */}
      <div
        aria-hidden
        className="pointer-events-none absolute rounded-full bg-ai-cyan/20 blur-xl"
        style={{ width: size * 0.55, height: size * 0.55 }}
      />

      {/* Tilting + floating 3D layer */}
      <motion.div
        className="relative"
        style={{ transformStyle: "preserve-3d" }}
        animate={
          reduce
            ? { rotateX: tilt.x, rotateY: tilt.y }
            : { rotateX: tilt.x, rotateY: tilt.y, y: [0, -6, 0] }
        }
        transition={{
          rotateX: { type: "spring", stiffness: 120, damping: 14 },
          rotateY: { type: "spring", stiffness: 120, damping: 14 },
          y: reduce
            ? { duration: 0 }
            : { duration: 5, repeat: Infinity, ease: "easeInOut" },
        }}
      >
        {/* Glassy translucent disc sitting just behind the ring for depth */}
        <div
          aria-hidden
          className="absolute inset-0 -z-10 rounded-full border border-white/60 bg-white/40 shadow-card backdrop-blur-sm"
          style={{ transform: "translateZ(-24px) scale(0.96)" }}
        />
        <div style={{ transform: "translateZ(28px)" }}>
          <ScoreRing score={score} label={label} size={size} />
        </div>
      </motion.div>
    </div>
  );
}
