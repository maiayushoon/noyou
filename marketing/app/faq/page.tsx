import type { Metadata } from "next";
import SectionHeading from "@/components/SectionHeading";
import FaqAccordion from "@/components/FaqAccordion";
import Cta from "@/components/Cta";
import JsonLd from "@/components/JsonLd";
import Reveal from "@/components/motion/Reveal";
import { FAQS } from "@/lib/content";
import { pageMetadata, faqPageJsonLd, breadcrumbJsonLd } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Frequently Asked Questions",
  description:
    "Answers about NoYou: what it is, how it works, what AEO/GEO (AI SEO) means, data privacy (GDPR/CCPA), the sources it scans, how the 0-100 reputation score is calculated, whether it can remove content, and pricing.",
  path: "/faq",
});

export default function FaqPage() {
  return (
    <>
      {/* Full FAQPage structured data — the primary GEO/AEO asset on this page. */}
      <JsonLd data={faqPageJsonLd(FAQS)} id="ld-faq" />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: "/" },
          { name: "FAQ", path: "/faq" },
        ])}
        id="ld-faq-breadcrumb"
      />

      <section className="bg-gradient-to-b from-brand-50 to-white py-16 sm:py-20">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              as="h1"
              eyebrow="FAQ"
              title="Frequently asked questions"
              description="Clear, direct answers about how NoYou works, how it protects your privacy, and how it helps you control your online and AI reputation."
            />
          </Reveal>
        </div>
      </section>

      <section className="pb-20">
        <div className="container-page">
          <Reveal>
            <FaqAccordion faqs={FAQS} />
          </Reveal>

          {/* Plain-text questions list improves crawlability and gives AI engines
              an unambiguous Q&A structure to cite. */}
          <Reveal
            delay={0.1}
            className="mx-auto mt-12 max-w-3xl rounded-2xl border border-slate-200 bg-slate-50 p-6"
          >
            <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-700">
              Still have questions?
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Reach the team at{" "}
              <a
                href="mailto:hello@noyou.app"
                className="font-semibold text-brand-700 hover:text-brand-800"
              >
                hello@noyou.app
              </a>{" "}
              and we’ll get back to you quickly.
            </p>
          </Reveal>
        </div>
      </section>

      <Cta />
    </>
  );
}
