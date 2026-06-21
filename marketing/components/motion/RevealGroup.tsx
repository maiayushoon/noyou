"use client";

import { motion, useReducedMotion, type Variants } from "framer-motion";
import type { ReactNode } from "react";

type RevealGroupProps = {
  children: ReactNode;
  className?: string;
  /** Seconds between each child reveal. */
  stagger?: number;
  as?: "div" | "ul" | "ol";
};

/**
 * Container that staggers the reveal of its direct <RevealItem> children when it
 * first scrolls into view. Pairs with RevealItem. Reduced-motion safe.
 */
export default function RevealGroup({
  children,
  className,
  stagger = 0.1,
  as = "div",
}: RevealGroupProps) {
  const reduceMotion = useReducedMotion();

  const container: Variants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: reduceMotion ? 0 : stagger,
      },
    },
  };

  const MotionTag = motion[as];

  return (
    <MotionTag
      className={className}
      variants={container}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "0px 0px -80px 0px" }}
    >
      {children}
    </MotionTag>
  );
}
