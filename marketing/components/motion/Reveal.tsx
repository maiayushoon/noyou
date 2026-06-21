"use client";

import { motion, useReducedMotion, type Variants } from "framer-motion";
import type { ReactNode } from "react";

type RevealProps = {
  children: ReactNode;
  /** Stagger delay in seconds, useful when revealing items in sequence. */
  delay?: number;
  /** Direction the element travels in from. */
  from?: "up" | "down" | "left" | "right" | "none";
  /** Extra classes applied to the wrapping element. */
  className?: string;
  /** Render as a different element (default div). */
  as?: "div" | "li" | "section" | "span";
};

const OFFSET = 24;

/**
 * Fades + slides its children into view the first time they scroll on screen.
 * Honors prefers-reduced-motion by rendering content statically (no transform).
 */
export default function Reveal({
  children,
  delay = 0,
  from = "up",
  className,
  as = "div",
}: RevealProps) {
  const reduceMotion = useReducedMotion();

  const initialOffset = {
    up: { y: OFFSET, x: 0 },
    down: { y: -OFFSET, x: 0 },
    left: { x: OFFSET, y: 0 },
    right: { x: -OFFSET, y: 0 },
    none: { x: 0, y: 0 },
  }[from];

  const variants: Variants = reduceMotion
    ? {
        hidden: { opacity: 1 },
        visible: { opacity: 1 },
      }
    : {
        hidden: { opacity: 0, ...initialOffset },
        visible: {
          opacity: 1,
          x: 0,
          y: 0,
          transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1], delay },
        },
      };

  const MotionTag = motion[as];

  return (
    <MotionTag
      className={className}
      variants={variants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "0px 0px -80px 0px" }}
    >
      {children}
    </MotionTag>
  );
}
