"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { SITE, STATS } from "@/lib/content";
import AvatarCluster from "@/components/AvatarCluster";
import ReputationOrb from "@/components/ReputationOrb";

/**
 * Home-page hero. The H1 states the product category and benefit in plain
 * language so both readers and AI answer engines get a direct, citable answer
 * to "what is NoYou?". The visual centerpiece is a floating, mouse-tilting 3D
 * reputation ring built from SVG + CSS layers (no WebGL).
 */
export default function Hero() {
  const reduceMotion = useReducedMotion();

  const container = {
    hidden: {},
    visible: {
      transition: { staggerChildren: reduceMotion ? 0 : 0.1, delayChildren: 0.05 },
    },
  };
  const item = reduceMotion
    ? { hidden: { opacity: 1 }, visible: { opacity: 1 } }
    : {
        hidden: { opacity: 0, y: 20 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
        },
      };

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-[#0b0b14] via-[#07070b] to-[#07070b]">
      {/* Animated soft gradient orbs in the background. */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-32 left-1/4 h-[28rem] w-[28rem] rounded-full bg-indigo-500/25 blur-3xl"
          animate={reduceMotion ? undefined : { y: [0, 24, 0], x: [0, 16, 0] }}
          transition={reduceMotion ? undefined : { duration: 14, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -right-24 top-10 h-[24rem] w-[24rem] rounded-full bg-cyan-500/20 blur-3xl"
          animate={reduceMotion ? undefined : { y: [0, -20, 0], x: [0, -14, 0] }}
          transition={reduceMotion ? undefined : { duration: 16, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-0 left-0 h-[22rem] w-[22rem] rounded-full bg-violet-500/20 blur-3xl"
          animate={reduceMotion ? undefined : { y: [0, -18, 0] }}
          transition={reduceMotion ? undefined : { duration: 18, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Subtle grid wash for depth. */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(99,102,241,0.12),transparent_55%)]" />
      </div>

      <div className="relative mx-auto grid max-w-content items-center gap-12 px-4 pb-20 pt-16 sm:px-6 sm:pt-20 lg:grid-cols-[1.05fr_1fr] lg:gap-8 lg:px-8 lg:pt-24">
        {/* Left column: copy + CTAs + trust. */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="visible"
          className="text-center lg:text-left"
        >
          <motion.span
            variants={item}
            className="inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.04] px-3 py-1 text-xs font-semibold text-indigo-200 shadow-sm backdrop-blur"
          >
            <Sparkles className="h-3.5 w-3.5 text-violet-400" aria-hidden="true" />
            New: AI Visibility Check for ChatGPT, Perplexity & Gemini
          </motion.span>

          <motion.h1
            variants={item}
            className="mt-6 text-balance text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl"
          >
            Own your online and{" "}
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-300 bg-clip-text text-transparent">
              AI reputation
            </span>
          </motion.h1>

          <motion.p
            variants={item}
            className="mx-auto mt-6 max-w-xl text-balance text-lg leading-relaxed text-slate-300 sm:text-xl lg:mx-0"
          >
            {SITE.name} is an AI-powered digital identity and reputation manager.
            It monitors the web and social for mentions of you, scores your
            reputation 0&ndash;100, flags high-risk content, and shows you how AI
            engines describe your brand.
          </motion.p>

          <motion.div
            variants={item}
            className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row lg:justify-start"
          >
            <a
              href={`${SITE.appUrl}/signup`}
              className="group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-ai-gradient px-6 py-3.5 text-base font-semibold text-white shadow-ai transition-transform duration-200 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 sm:w-auto"
            >
              Start free — no card required
              <ArrowRight
                className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </a>
            <a
              href="/features"
              className="inline-flex w-full items-center justify-center rounded-xl border border-white/15 bg-white/[0.04] px-6 py-3.5 text-base font-semibold text-slate-100 backdrop-blur transition-colors hover:border-white/25 hover:bg-white/[0.06] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-indigo sm:w-auto"
            >
              See how it works
            </a>
          </motion.div>

          <motion.div variants={item} className="mt-8 flex justify-center lg:justify-start">
            <AvatarCluster caption="10,000+ reputations protected — founders, execs & brands." />
          </motion.div>
        </motion.div>

        {/* Right column: the 3D centerpiece. */}
        <motion.div
          initial={reduceMotion ? { opacity: 1 } : { opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={reduceMotion ? { duration: 0 } : { duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
          className="relative"
        >
          <ReputationOrb />
        </motion.div>
      </div>

      {/* Stat band */}
      <div className="relative mx-auto max-w-content px-4 pb-16 sm:px-6 lg:px-8">
        <motion.dl
          variants={container}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "0px 0px -60px 0px" }}
          className="mx-auto grid max-w-5xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.06] backdrop-blur-sm sm:grid-cols-4"
        >
          {STATS.map((stat) => (
            <motion.div
              key={stat.label}
              variants={item}
              className="group bg-[#08080d] p-5 text-center transition-colors hover:bg-white/[0.04]"
            >
              <dt className="sr-only">{stat.label}</dt>
              <dd>
                <span className="block bg-gradient-to-br from-indigo-400 to-cyan-300 bg-clip-text text-2xl font-bold text-transparent">
                  {stat.value}
                </span>
                <span className="mt-1 block text-xs leading-snug text-slate-400">
                  {stat.label}
                </span>
              </dd>
            </motion.div>
          ))}
        </motion.dl>
      </div>
    </section>
  );
}
