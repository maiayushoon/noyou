import type { Metadata } from "next";
import Link from "next/link";
import Hero from "@/components/Hero";
import SectionHeading from "@/components/SectionHeading";
import FeatureGrid from "@/components/FeatureGrid";
import PricingTable from "@/components/PricingTable";
import FaqAccordion from "@/components/FaqAccordion";
import Cta from "@/components/Cta";
import JsonLd from "@/components/JsonLd";
import Reveal from "@/components/motion/Reveal";
import RevealGroup from "@/components/motion/RevealGroup";
import RevealItem from "@/components/motion/RevealItem";
import {
  FEATURES,
  HOW_IT_WORKS,
  FAQS,
  SITE,
} from "@/lib/content";
import {
  pageMetadata,
  softwareApplicationJsonLd,
  faqPageJsonLd,
} from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "AI-Powered Reputation & Digital Identity Management",
  description:
    "NoYou monitors the web and social for mentions of you, runs AI sentiment and risk analysis, scores your reputation 0-100, alerts you to high-risk content, and shows how AI engines describe your brand. Start free.",
  path: "/",
});

const homeFaqs = FAQS.slice(0, 5);

export default function HomePage() {
  return (
    <>
      <JsonLd data={softwareApplicationJsonLd()} id="ld-software" />
      <JsonLd data={faqPageJsonLd(homeFaqs)} id="ld-home-faq" />

      <Hero />

      {/* Social proof / who it's for */}
      <section className="border-y border-white/[0.06] bg-white/[0.02] py-10">
        <div className="container-page">
          <Reveal>
            <p className="text-center text-sm font-medium uppercase tracking-wider text-slate-400">
              Trusted by founders, executives, professionals, and brands
            </p>
          </Reveal>
          <RevealGroup
            className="mx-auto mt-6 grid max-w-4xl grid-cols-2 gap-4 sm:grid-cols-4"
            stagger={0.08}
          >
            {["Founders", "Executives", "Professionals", "Brands & Agencies"].map(
              (audience) => (
                <RevealItem
                  key={audience}
                  className="rounded-xl border border-white/[0.06] bg-white/[0.03] px-4 py-3 text-center text-sm font-semibold text-slate-200 backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-white/[0.12] hover:shadow-ai-glow"
                >
                  {audience}
                </RevealItem>
              ),
            )}
          </RevealGroup>
        </div>
      </section>

      {/* Feature grid */}
      <section className="py-20">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Everything in one place"
              title="One platform to watch, score, and protect your reputation"
              description="NoYou turns scattered mentions into a clear picture — and tells you exactly what to do next."
            />
          </Reveal>
          <div className="mt-12">
            <FeatureGrid features={FEATURES} />
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative overflow-hidden border-y border-white/[0.06] bg-white/[0.02] py-20 text-white">
        {/* Soft ai-gradient orb for depth. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-0 h-72 w-[40rem] -translate-x-1/2 rounded-full bg-ai-violet/10 blur-3xl"
        />
        <div className="container-page relative">
          <Reveal>
            <SectionHeading
              eyebrow="How it works"
              title={<span className="text-white">From mention to action in four steps</span>}
              description={
                <span className="text-slate-400">
                  Set it up in minutes. NoYou does the watching, the scoring, and
                  the recommending.
                </span>
              }
            />
          </Reveal>
          <RevealGroup
            as="ol"
            className="mx-auto mt-12 grid max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-4"
            stagger={0.1}
          >
            {HOW_IT_WORKS.map((step) => (
              <RevealItem
                key={step.number}
                as="li"
                className="rounded-xl border border-white/[0.06] bg-white/[0.03] p-6 backdrop-blur-sm transition-all hover:-translate-y-1 hover:border-white/[0.12] hover:shadow-ai-glow"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-ai-gradient text-base font-bold text-white shadow-ai">
                  {step.number}
                </span>
                <h3 className="mt-4 text-lg font-semibold text-white">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">
                  {step.description}
                </p>
              </RevealItem>
            ))}
          </RevealGroup>
        </div>
      </section>

      {/* AI Visibility highlight */}
      <section className="py-20">
        <div className="container-page">
          <div className="grid items-center gap-10 rounded-2xl border border-white/[0.06] bg-white/[0.03] p-8 shadow-ai backdrop-blur-sm lg:grid-cols-2 lg:p-12">
            <Reveal from="right">
              <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-cyan-300">
                New · AI Visibility
              </p>
              <h2 className="text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Find out how AI engines describe you
              </h2>
              <p className="mt-4 text-lg leading-relaxed text-slate-300">
                People now meet your brand inside an AI answer before they ever
                visit your site. The AI Visibility Check asks ChatGPT, Perplexity,
                Gemini, and Google AI Overviews how they describe you, surfaces
                inaccuracies, and recommends content to publish so they cite the
                right facts.
              </p>
              <ul className="mt-6 space-y-3">
                {[
                  "See what each AI engine says about your name or brand",
                  "Spot outdated or false claims before customers do",
                  "Get a content plan to shape future AI answers (GEO/AEO)",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-slate-300">
                    <span
                      aria-hidden="true"
                      className="mt-1 flex h-5 w-5 flex-none items-center justify-center rounded-full bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30"
                    >
                      ✓
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link
                  href="/features#ai-visibility"
                  className="inline-flex items-center gap-1 rounded-lg bg-ai-gradient px-5 py-3 text-base font-semibold text-white shadow-ai transition-transform hover:-translate-y-0.5"
                >
                  Explore AI Visibility
                  <span aria-hidden="true">→</span>
                </Link>
              </div>
            </Reveal>

            {/* Illustrative mock answer card */}
            <Reveal from="left" className="rounded-xl border border-white/[0.06] bg-white/[0.05] p-6 shadow-ai backdrop-blur-sm transition-all hover:border-white/[0.12]">
              <div className="flex items-center gap-2 border-b border-white/[0.08] pb-4">
                <span className="h-2.5 w-2.5 rounded-full bg-cyan-400" />
                <span className="text-sm font-semibold text-white">
                  AI Visibility report
                </span>
                <span className="ml-auto rounded-full bg-white/[0.06] px-2 py-0.5 text-xs font-medium text-slate-300">
                  4 engines
                </span>
              </div>
              <dl className="mt-4 space-y-4 text-sm">
                <div>
                  <dt className="font-semibold text-slate-100">ChatGPT</dt>
                  <dd className="text-slate-400">
                    Describes you accurately. Cites your homepage and About page.
                  </dd>
                </div>
                <div>
                  <dt className="font-semibold text-slate-100">Perplexity</dt>
                  <dd className="text-slate-400">
                    Uses a two-year-old funding figure.{" "}
                    <span className="font-medium text-amber-300">
                      Recommend: publish an updated facts page.
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="font-semibold text-slate-100">Gemini</dt>
                  <dd className="text-slate-400">
                    Confuses you with a similarly named company.{" "}
                    <span className="font-medium text-red-300">
                      Action: add clear entity markup.
                    </span>
                  </dd>
                </div>
              </dl>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Pricing teaser */}
      <section className="border-y border-white/[0.06] bg-white/[0.02] py-20">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Pricing"
              title="Plans for every stage"
              description="Start free. Upgrade when you need deeper coverage, faster scans, and AI Visibility."
            />
          </Reveal>
          <div className="mt-12">
            <PricingTable />
          </div>
          <p className="mt-8 text-center text-sm text-slate-500">
            All prices in USD.{" "}
            <Link href="/pricing" className="font-semibold text-indigo-300 hover:text-indigo-200">
              Compare plans in detail →
            </Link>
          </p>
        </div>
      </section>

      {/* FAQ teaser */}
      <section className="py-20">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="FAQ"
              title="Answers to common questions"
              description="The essentials on what NoYou is, how it works, and how it protects your privacy."
            />
          </Reveal>
          <Reveal delay={0.1} className="mt-12">
            <FaqAccordion faqs={homeFaqs} />
          </Reveal>
          <p className="mt-8 text-center text-sm text-slate-500">
            <Link href="/faq" className="font-semibold text-indigo-300 hover:text-indigo-200">
              Read all FAQs →
            </Link>
          </p>
        </div>
      </section>

      <Cta />
    </>
  );
}
