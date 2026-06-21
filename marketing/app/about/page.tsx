import type { Metadata } from "next";
import SectionHeading from "@/components/SectionHeading";
import Cta from "@/components/Cta";
import JsonLd from "@/components/JsonLd";
import Reveal from "@/components/motion/Reveal";
import RevealGroup from "@/components/motion/RevealGroup";
import RevealItem from "@/components/motion/RevealItem";
import { ABOUT, SITE } from "@/lib/content";
import { pageMetadata, organizationJsonLd, breadcrumbJsonLd } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "About NoYou",
  description:
    "NoYou is an AI-powered digital identity and reputation management company on a mission to help people and brands control their narrative across the web and AI answer engines — accurately, affordably, and privately.",
  path: "/about",
  ogType: "article",
});

export default function AboutPage() {
  return (
    <>
      <JsonLd data={organizationJsonLd()} id="ld-about-org" />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: "/" },
          { name: "About", path: "/about" },
        ])}
        id="ld-about-breadcrumb"
      />

      <section className="bg-gradient-to-b from-brand-50 to-white py-16 sm:py-20">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              as="h1"
              eyebrow="About"
              title="We help you control your narrative"
              description={ABOUT.mission}
            />
          </Reveal>
        </div>
      </section>

      {/* Story */}
      <section className="py-16">
        <div className="container-page">
          <Reveal className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-bold tracking-tight text-brand-900 sm:text-3xl">
              Our story
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-600">
              {ABOUT.story}
            </p>
          </Reveal>
        </div>
      </section>

      {/* Values */}
      <section className="bg-slate-50 py-16">
        <div className="container-page">
          <Reveal>
            <SectionHeading eyebrow="What we believe" title="Our values" />
          </Reveal>
          <RevealGroup
            className="mx-auto mt-10 grid max-w-4xl gap-6 sm:grid-cols-2"
            stagger={0.08}
          >
            {ABOUT.values.map((value) => (
              <RevealItem
                key={value.title}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card transition-all hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-ai"
              >
                <h3 className="text-lg font-semibold text-brand-900">
                  {value.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {value.description}
                </p>
              </RevealItem>
            ))}
          </RevealGroup>
        </div>
      </section>

      {/* Privacy */}
      <section id="privacy" className="py-16">
        <div className="container-page">
          <Reveal className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-bold tracking-tight text-brand-900 sm:text-3xl">
              Privacy & compliance
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-600">
              {SITE.name} analyzes publicly available mentions — not private
              accounts or messages. We support GDPR and CCPA data-subject requests,
              including access and erasure, and you can export or delete your data
              at any time. For privacy-sensitive teams, the scanning engine can run
              fully offline using keyless sources, so no data leaves your
              environment. We never sell your data.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Terms */}
      <section id="terms" className="border-t border-slate-100 py-16">
        <div className="container-page">
          <Reveal className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-bold tracking-tight text-brand-900 sm:text-3xl">
              Terms & responsible use
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-slate-600">
              {SITE.name} is a tool for monitoring and improving your own
              reputation, or that of a brand you are authorized to represent. It is
              not for surveilling or harassing others. By using {SITE.name} you
              agree to use it lawfully and in accordance with the terms of the
              sources it scans. Recommendations are guidance, not legal advice;
              consult a qualified professional for legal matters.
            </p>
            <p className="mt-4 text-sm text-slate-500">
              Questions about privacy, terms, or data requests? Email{" "}
              <a
                href={`mailto:${SITE.email}`}
                className="font-semibold text-brand-700 hover:text-brand-800"
              >
                {SITE.email}
              </a>
              .
            </p>
          </Reveal>
        </div>
      </section>

      <Cta
        title="Ready to see where you stand?"
        description="Start free and get your reputation score, risk alerts, and AI Visibility report in minutes."
      />
    </>
  );
}
