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
      <section className="border-y border-slate-100 bg-slate-50/60 py-10">
        <div className="container-page">
          <Reveal>
            <p className="text-center text-sm font-medium uppercase tracking-wider text-slate-500">
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
                  className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-center text-sm font-semibold text-brand-800 shadow-sm transition-all hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-card"
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
      <section className="bg-brand-900 py-20 text-white">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="How it works"
              title={<span className="text-white">From mention to action in four steps</span>}
              description={
                <span className="text-brand-100">
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
                className="rounded-2xl border border-white/10 bg-white/5 p-6 transition-colors hover:border-white/25 hover:bg-white/10"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-indigo-400 to-cyan-400 text-base font-bold text-brand-950 shadow-ai">
                  {step.number}
                </span>
                <h3 className="mt-4 text-lg font-semibold text-white">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-brand-100">
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
          <div className="grid items-center gap-10 rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-brand-50 p-8 shadow-card lg:grid-cols-2 lg:p-12">
            <Reveal from="right">
              <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-accent-600">
                New · AI Visibility
              </p>
              <h2 className="text-balance text-3xl font-bold tracking-tight text-brand-900 sm:text-4xl">
                Find out how AI engines describe you
              </h2>
              <p className="mt-4 text-lg leading-relaxed text-slate-600">
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
                  <li key={item} className="flex items-start gap-3 text-slate-700">
                    <span
                      aria-hidden="true"
                      className="mt-1 flex h-5 w-5 flex-none items-center justify-center rounded-full bg-accent-100 text-accent-700"
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
                  className="inline-flex items-center gap-1 rounded-lg bg-brand-600 px-5 py-3 text-base font-semibold text-white shadow-sm transition-colors hover:bg-brand-700"
                >
                  Explore AI Visibility
                  <span aria-hidden="true">→</span>
                </Link>
              </div>
            </Reveal>

            {/* Illustrative mock answer card */}
            <Reveal from="left" className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lift transition-shadow hover:shadow-ai">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
                <span className="h-2.5 w-2.5 rounded-full bg-accent-500" />
                <span className="text-sm font-semibold text-brand-900">
                  AI Visibility report
                </span>
                <span className="ml-auto rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">
                  4 engines
                </span>
              </div>
              <dl className="mt-4 space-y-4 text-sm">
                <div>
                  <dt className="font-semibold text-slate-800">ChatGPT</dt>
                  <dd className="text-slate-600">
                    Describes you accurately. Cites your homepage and About page.
                  </dd>
                </div>
                <div>
                  <dt className="font-semibold text-slate-800">Perplexity</dt>
                  <dd className="text-slate-600">
                    Uses a two-year-old funding figure.{" "}
                    <span className="font-medium text-amber-600">
                      Recommend: publish an updated facts page.
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="font-semibold text-slate-800">Gemini</dt>
                  <dd className="text-slate-600">
                    Confuses you with a similarly named company.{" "}
                    <span className="font-medium text-red-600">
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
      <section className="bg-slate-50 py-20">
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
            <Link href="/pricing" className="font-semibold text-brand-700 hover:text-brand-800">
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
            <Link href="/faq" className="font-semibold text-brand-700 hover:text-brand-800">
              Read all FAQs →
            </Link>
          </p>
        </div>
      </section>

      <Cta />
    </>
  );
}
