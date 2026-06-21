import type { Metadata } from "next";
import Link from "next/link";
import SectionHeading from "@/components/SectionHeading";
import FeatureGrid from "@/components/FeatureGrid";
import Cta from "@/components/Cta";
import JsonLd from "@/components/JsonLd";
import Reveal from "@/components/motion/Reveal";
import RevealGroup from "@/components/motion/RevealGroup";
import RevealItem from "@/components/motion/RevealItem";
import { FEATURES, HOW_IT_WORKS, DATA_SOURCES, SITE } from "@/lib/content";
import { pageMetadata, breadcrumbJsonLd } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Features",
  description:
    "Explore NoYou's features: web and social monitoring, AI sentiment and risk analysis, a 0-100 reputation score, high-risk alerts, suggested cleanup actions, the predictive Pre-Post Check, and the AI Visibility Check.",
  path: "/features",
});

export default function FeaturesPage() {
  return (
    <>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: "/" },
          { name: "Features", path: "/features" },
        ])}
        id="ld-features-breadcrumb"
      />

      <section className="relative overflow-hidden bg-gradient-to-b from-[#1A160F] to-[#12100D] py-16 sm:py-20">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-0 h-64 w-[40rem] -translate-x-1/2 rounded-full bg-ai-indigo/10 blur-3xl"
        />
        <div className="container-page relative">
          <Reveal>
            <SectionHeading
              as="h1"
              eyebrow="Features"
              title="Everything you need to manage your reputation"
              description="NoYou combines real-time monitoring, AI analysis, and clear recommendations so you always know where you stand — and what to do next."
            />
          </Reveal>
        </div>
      </section>

      <section className="pb-20">
        <div className="container-page">
          <FeatureGrid features={FEATURES} detailed />
        </div>
      </section>

      {/* Pre-Post Check deep dive */}
      <section id="pre-post-check" className="border-y border-white/[0.06] bg-white/[0.02] py-20">
        <div className="container-page grid items-center gap-10 lg:grid-cols-2">
          <Reveal from="right">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-amber-200">
              Predictive
            </p>
            <h2 className="text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Pre-Post Check: will this post hurt me?
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-300">
              Reputation damage is far cheaper to prevent than to repair. Paste a
              draft tweet, comment, or announcement into Pre-Post Check and NoYou
              estimates its reputational risk, highlights wording that could be
              misread or spark backlash, and suggests safer phrasing — before you
              hit publish.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "Risk estimate for any draft, in seconds",
                "Flags ambiguous or inflammatory wording",
                "Suggests safer alternative phrasing",
                "Learns the tone that fits your brand",
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
          </Reveal>
          <Reveal
            from="left"
            className="rounded-xl border border-white/[0.06] bg-white/[0.03] p-6 shadow-ai backdrop-blur-sm transition-all hover:border-white/[0.12]"
          >
            <div className="rounded-xl border border-white/[0.06] bg-white/[0.04] p-4 text-sm text-slate-300">
              “Honestly our competitor’s product is a joke and anyone who buys it
              is wasting their money.”
            </div>
            <div className="mt-4 flex items-center justify-between rounded-xl border border-amber-500/30 bg-amber-500/15 px-4 py-3">
              <span className="text-sm font-semibold text-amber-300">
                Risk: High
              </span>
              <span className="text-xs text-amber-200/80">Insulting customers</span>
            </div>
            <p className="mt-4 text-sm text-slate-400">
              <span className="font-semibold text-slate-100">Suggested rewrite:</span>{" "}
              “We think we offer a better value — here’s an honest comparison so
              you can decide for yourself.”
            </p>
          </Reveal>
        </div>
      </section>

      {/* AI Visibility deep dive */}
      <section id="ai-visibility" className="py-20">
        <div className="container-page grid items-center gap-10 lg:grid-cols-2">
          <Reveal
            from="right"
            className="order-2 lg:order-1 rounded-xl border border-white/[0.06] bg-white/[0.03] p-6 shadow-ai backdrop-blur-sm transition-all hover:border-white/[0.12]"
          >
            <h3 className="text-sm font-semibold text-white">
              How AI engines describe “{SITE.name}”
            </h3>
            <dl className="mt-4 space-y-4 text-sm">
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.04] p-4">
                <dt className="font-semibold text-slate-100">ChatGPT & Perplexity</dt>
                <dd className="mt-1 text-slate-400">
                  Accurate summary, correct pricing, cites your homepage.
                </dd>
              </div>
              <div className="rounded-xl border border-amber-500/30 bg-amber-500/15 p-4">
                <dt className="font-semibold text-amber-300">Gemini</dt>
                <dd className="mt-1 text-amber-200/80">
                  Missing your newest feature — publish a feature page to fix.
                </dd>
              </div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.04] p-4">
                <dt className="font-semibold text-slate-100">Google AI Overviews</dt>
                <dd className="mt-1 text-slate-400">
                  Surfaces your FAQ. Add structured data to strengthen citations.
                </dd>
              </div>
            </dl>
          </Reveal>
          <Reveal from="left" className="order-1 lg:order-2">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-amber-200">
              AEO / GEO
            </p>
            <h2 className="text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl">
              AI Visibility Check
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-300">
              Answer Engine Optimization (AEO) and Generative Engine Optimization
              (GEO) — AI SEO — are about making sure AI answer engines surface and
              cite accurate information about you. NoYou queries the major engines,
              shows you exactly how they describe your brand, flags errors, and
              gives you a concrete content plan to shape future answers.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "Checks ChatGPT, Perplexity, Gemini, and Google AI Overviews",
                "Highlights inaccurate, outdated, or missing facts",
                "Recommends pages and structured data to publish",
                "Tracks how AI answers change over time",
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
          </Reveal>
        </div>
      </section>

      {/* Data sources */}
      <section className="relative overflow-hidden border-y border-white/[0.06] bg-white/[0.02] py-20 text-white">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute right-0 top-0 h-72 w-[36rem] rounded-full bg-ai-cyan/8 blur-3xl"
        />
        <div className="container-page relative">
          <Reveal>
            <SectionHeading
              eyebrow="Data sources"
              title={<span className="text-white">Real sources, no keys required to start</span>}
              description={
                <span className="text-slate-400">
                  NoYou works with public, keyless sources out of the box. Add Google
                  CSE and LLM providers when you want deeper coverage.
                </span>
              }
            />
          </Reveal>
          <Reveal
            delay={0.1}
            className="mx-auto mt-12 max-w-3xl overflow-hidden rounded-xl border border-white/[0.08] bg-white/[0.03] backdrop-blur-sm"
          >
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.04] text-slate-400">
                <tr>
                  <th scope="col" className="px-5 py-3 font-semibold">Source</th>
                  <th scope="col" className="px-5 py-3 font-semibold">Type</th>
                  <th scope="col" className="px-5 py-3 font-semibold">Setup</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06]">
                {DATA_SOURCES.map((source) => (
                  <tr key={source.name}>
                    <th scope="row" className="px-5 py-3 font-medium text-white">
                      {source.name}
                    </th>
                    <td className="px-5 py-3 text-slate-400">{source.type}</td>
                    <td className="px-5 py-3">
                      {source.keyless ? (
                        <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-semibold text-emerald-300 ring-1 ring-emerald-500/30">
                          No API key
                        </span>
                      ) : (
                        <span className="rounded-full bg-white/[0.06] px-2.5 py-0.5 text-xs font-semibold text-slate-300">
                          Optional key
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Reveal>
        </div>
      </section>

      {/* How it works recap */}
      <section className="py-20">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Workflow"
              title="How NoYou works, end to end"
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
          <Reveal>
            <p className="mt-10 text-center text-sm text-slate-500">
              Ready to see your score?{" "}
              <Link href="/pricing" className="font-semibold text-amber-200 hover:text-amber-100">
                View pricing →
              </Link>
            </p>
          </Reveal>
        </div>
      </section>

      <Cta />
    </>
  );
}
