import type { Metadata } from "next";
import SectionHeading from "@/components/SectionHeading";
import PricingTable from "@/components/PricingTable";
import FaqAccordion from "@/components/FaqAccordion";
import Cta from "@/components/Cta";
import JsonLd from "@/components/JsonLd";
import Reveal from "@/components/motion/Reveal";
import RevealGroup from "@/components/motion/RevealGroup";
import RevealItem from "@/components/motion/RevealItem";
import { FAQS } from "@/lib/content";
import {
  pageMetadata,
  softwareApplicationJsonLd,
  breadcrumbJsonLd,
  faqPageJsonLd,
} from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Pricing — Free, Pro $29, Premium $59, Enterprise",
  description:
    "Simple, transparent pricing for NoYou. Start free forever. Pro is $29/mo, Premium is $59/mo, and Enterprise is custom. Compare reputation monitoring, AI analysis, alerts, and AI Visibility across plans.",
  path: "/pricing",
});

// Pricing-relevant FAQs for the bottom of the page.
const pricingFaqs = FAQS.filter((f) =>
  ["pricing", "privacy", "remove-content"].includes(f.id),
);

export default function PricingPage() {
  return (
    <>
      {/* SoftwareApplication carries the Offer data (price/currency) for each plan. */}
      <JsonLd data={softwareApplicationJsonLd()} id="ld-pricing-software" />
      <JsonLd data={faqPageJsonLd(pricingFaqs)} id="ld-pricing-faq" />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: "/" },
          { name: "Pricing", path: "/pricing" },
        ])}
        id="ld-pricing-breadcrumb"
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
              eyebrow="Pricing"
              title="Simple, transparent pricing"
              description="Start free and upgrade when you need deeper coverage, faster scans, and AI Visibility. All prices in USD. No hidden fees."
            />
          </Reveal>
        </div>
      </section>

      <section className="pb-16">
        <div className="container-page">
          <PricingTable />
        </div>
      </section>

      {/* Comparison highlights */}
      <section className="border-y border-white/[0.06] bg-white/[0.02] py-16">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="What changes as you grow"
              title="Pick the plan that matches your risk"
            />
          </Reveal>
          <RevealGroup
            className="mx-auto mt-10 grid max-w-4xl gap-6 sm:grid-cols-3"
            stagger={0.08}
          >
            {[
              {
                title: "Coverage",
                free: "Weekly scans, 1 identity",
                pro: "Daily scans, 3 identities",
                premium: "Hourly scans, 10 identities",
              },
              {
                title: "AI analysis",
                free: "Basic sentiment",
                pro: "Full sentiment + risk",
                premium: "Full + weekly AI Visibility",
              },
              {
                title: "Alerts",
                free: "In-app only",
                pro: "Email high-risk alerts",
                premium: "Real-time alerts",
              },
            ].map((row) => (
              <RevealItem
                key={row.title}
                className="rounded-xl border border-white/[0.06] bg-white/[0.03] p-6 backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-white/[0.12] hover:shadow-ai-glow"
              >
                <h3 className="text-sm font-semibold uppercase tracking-wide text-amber-200">
                  {row.title}
                </h3>
                <dl className="mt-4 space-y-3 text-sm">
                  <div className="flex justify-between gap-3">
                    <dt className="text-slate-500">Free</dt>
                    <dd className="text-right font-medium text-slate-200">{row.free}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-slate-500">Pro</dt>
                    <dd className="text-right font-medium text-slate-200">{row.pro}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-slate-500">Premium</dt>
                    <dd className="text-right font-medium text-slate-200">{row.premium}</dd>
                  </div>
                </dl>
              </RevealItem>
            ))}
          </RevealGroup>
        </div>
      </section>

      {/* Pricing FAQ */}
      <section className="py-16">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Pricing FAQ"
              title="Questions about plans & billing"
            />
          </Reveal>
          <Reveal delay={0.1} className="mt-10">
            <FaqAccordion faqs={pricingFaqs} />
          </Reveal>
        </div>
      </section>

      <Cta
        title="Try NoYou free — upgrade anytime"
        description="The Free plan is genuinely useful: monitor one identity, see your reputation score, and run AI risk analysis with keyless sources."
      />
    </>
  );
}
