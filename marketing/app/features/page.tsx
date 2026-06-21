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

      <section className="bg-gradient-to-b from-brand-50 to-white py-16 sm:py-20">
        <div className="container-page">
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
      <section id="pre-post-check" className="bg-slate-50 py-20">
        <div className="container-page grid items-center gap-10 lg:grid-cols-2">
          <Reveal from="right">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-accent-600">
              Predictive
            </p>
            <h2 className="text-balance text-3xl font-bold tracking-tight text-brand-900 sm:text-4xl">
              Pre-Post Check: will this post hurt me?
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-600">
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
          </Reveal>
          <Reveal
            from="left"
            className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lift transition-shadow hover:shadow-ai"
          >
            <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
              “Honestly our competitor’s product is a joke and anyone who buys it
              is wasting their money.”
            </div>
            <div className="mt-4 flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
              <span className="text-sm font-semibold text-amber-800">
                Risk: High
              </span>
              <span className="text-xs text-amber-700">Insulting customers</span>
            </div>
            <p className="mt-4 text-sm text-slate-600">
              <span className="font-semibold text-brand-900">Suggested rewrite:</span>{" "}
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
            className="order-2 lg:order-1 rounded-2xl border border-slate-200 bg-white p-6 shadow-lift transition-shadow hover:shadow-ai"
          >
            <h3 className="text-sm font-semibold text-brand-900">
              How AI engines describe “{SITE.name}”
            </h3>
            <dl className="mt-4 space-y-4 text-sm">
              <div className="rounded-xl bg-slate-50 p-4">
                <dt className="font-semibold text-slate-800">ChatGPT & Perplexity</dt>
                <dd className="mt-1 text-slate-600">
                  Accurate summary, correct pricing, cites your homepage.
                </dd>
              </div>
              <div className="rounded-xl bg-amber-50 p-4">
                <dt className="font-semibold text-amber-800">Gemini</dt>
                <dd className="mt-1 text-amber-700">
                  Missing your newest feature — publish a feature page to fix.
                </dd>
              </div>
              <div className="rounded-xl bg-slate-50 p-4">
                <dt className="font-semibold text-slate-800">Google AI Overviews</dt>
                <dd className="mt-1 text-slate-600">
                  Surfaces your FAQ. Add structured data to strengthen citations.
                </dd>
              </div>
            </dl>
          </Reveal>
          <Reveal from="left" className="order-1 lg:order-2">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-accent-600">
              AEO / GEO
            </p>
            <h2 className="text-balance text-3xl font-bold tracking-tight text-brand-900 sm:text-4xl">
              AI Visibility Check
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-600">
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
          </Reveal>
        </div>
      </section>

      {/* Data sources */}
      <section className="bg-brand-900 py-20 text-white">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Data sources"
              title={<span className="text-white">Real sources, no keys required to start</span>}
              description={
                <span className="text-brand-100">
                  NoYou works with public, keyless sources out of the box. Add Google
                  CSE and LLM providers when you want deeper coverage.
                </span>
              }
            />
          </Reveal>
          <Reveal
            delay={0.1}
            className="mx-auto mt-12 max-w-3xl overflow-hidden rounded-2xl border border-white/10"
          >
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-brand-100">
                <tr>
                  <th scope="col" className="px-5 py-3 font-semibold">Source</th>
                  <th scope="col" className="px-5 py-3 font-semibold">Type</th>
                  <th scope="col" className="px-5 py-3 font-semibold">Setup</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {DATA_SOURCES.map((source) => (
                  <tr key={source.name}>
                    <th scope="row" className="px-5 py-3 font-medium text-white">
                      {source.name}
                    </th>
                    <td className="px-5 py-3 text-brand-100">{source.type}</td>
                    <td className="px-5 py-3">
                      {source.keyless ? (
                        <span className="rounded-full bg-accent-500/20 px-2.5 py-0.5 text-xs font-semibold text-accent-200">
                          No API key
                        </span>
                      ) : (
                        <span className="rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-semibold text-brand-100">
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
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card transition-all hover:-translate-y-1 hover:border-indigo-200 hover:shadow-ai"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-ai-gradient text-base font-bold text-white shadow-ai">
                  {step.number}
                </span>
                <h3 className="mt-4 text-lg font-semibold text-brand-900">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {step.description}
                </p>
              </RevealItem>
            ))}
          </RevealGroup>
          <Reveal>
            <p className="mt-10 text-center text-sm text-slate-500">
              Ready to see your score?{" "}
              <Link href="/pricing" className="font-semibold text-brand-700 hover:text-brand-800">
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
