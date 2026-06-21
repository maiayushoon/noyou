"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useState } from "react";

type AvatarSpec = {
  /** pravatar image index (1..70). */
  img: number;
  /** Initials shown if the image fails to load. */
  initials: string;
  /** Tailwind gradient classes for the fallback chip. */
  gradient: string;
  /** Decorative alt text. */
  label: string;
};

const AVATARS: AvatarSpec[] = [
  { img: 12, initials: "AR", gradient: "from-indigo-500 to-violet-500", label: "NoYou member" },
  { img: 32, initials: "JL", gradient: "from-violet-500 to-fuchsia-500", label: "NoYou member" },
  { img: 5, initials: "MP", gradient: "from-cyan-500 to-sky-500", label: "NoYou member" },
  { img: 47, initials: "SK", gradient: "from-sky-500 to-indigo-500", label: "NoYou member" },
  { img: 60, initials: "DT", gradient: "from-fuchsia-500 to-rose-500", label: "NoYou member" },
];

function Avatar({ spec, index }: { spec: AvatarSpec; index: number }) {
  const [failed, setFailed] = useState(false);

  return (
    <span
      className="relative inline-flex h-11 w-11 items-center justify-center overflow-hidden rounded-full ring-2 ring-white/15 shadow-card"
      style={{ zIndex: AVATARS.length - index }}
    >
      {failed ? (
        <span
          aria-hidden="true"
          className={`flex h-full w-full items-center justify-center bg-gradient-to-br ${spec.gradient} text-xs font-bold text-white`}
        >
          {spec.initials}
        </span>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={`https://i.pravatar.cc/96?img=${spec.img}`}
          alt={spec.label}
          width={44}
          height={44}
          loading="lazy"
          onError={() => setFailed(true)}
          className="h-full w-full object-cover"
        />
      )}
    </span>
  );
}

type AvatarClusterProps = {
  /** Trust copy shown beside the stack, e.g. "10,000+ reputations protected". */
  caption: string;
  className?: string;
};

/**
 * Overlapping stack of user avatars conveying real people using NoYou.
 * Each avatar floats gently (reduced-motion safe) and falls back to a
 * gradient-initial chip if its placeholder photo fails to load.
 */
export default function AvatarCluster({ caption, className = "" }: AvatarClusterProps) {
  const reduceMotion = useReducedMotion();

  return (
    <div className={`flex items-center gap-4 ${className}`}>
      <div className="flex -space-x-3">
        {AVATARS.map((spec, index) => (
          <motion.div
            key={spec.img}
            animate={
              reduceMotion
                ? undefined
                : { y: [0, -5, 0] }
            }
            transition={
              reduceMotion
                ? undefined
                : {
                    duration: 3.5 + index * 0.4,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: index * 0.15,
                  }
            }
          >
            <Avatar spec={spec} index={index} />
          </motion.div>
        ))}
      </div>
      <p className="text-left text-sm font-medium leading-snug text-slate-400">
        {caption}
      </p>
    </div>
  );
}
