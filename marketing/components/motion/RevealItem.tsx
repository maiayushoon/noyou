"use client";

import { motion, useReducedMotion, type Variants } from "framer-motion";
import type { ReactNode } from "react";

type RevealItemProps = {
  children: ReactNode;
  className?: string;
  as?: "div" | "li" | "article";
};

/**
 * A single staggered child for use inside <RevealGroup>. It reads its hidden /
 * visible state from the parent group, so the parent controls timing.
 */
export default function RevealItem({
  children,
  className,
  as = "div",
}: RevealItemProps) {
  const reduceMotion = useReducedMotion();

  const variants: Variants = reduceMotion
    ? { hidden: { opacity: 1 }, visible: { opacity: 1 } }
    : {
        hidden: { opacity: 0, y: 22 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
        },
      };

  const MotionTag = motion[as];

  return (
    <MotionTag className={className} variants={variants}>
      {children}
    </MotionTag>
  );
}
