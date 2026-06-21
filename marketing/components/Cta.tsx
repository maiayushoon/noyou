import { SITE } from "@/lib/content";

type CtaProps = {
  title?: string;
  description?: string;
  primaryLabel?: string;
  primaryHref?: string;
  secondaryLabel?: string;
  secondaryHref?: string;
};

/** Conversion call-to-action band, reused across pages. */
export default function Cta({
  title = "Take control of your reputation today",
  description = "Start free in minutes. See your reputation score, catch high-risk mentions, and find out how AI engines describe you.",
  primaryLabel = "Start free",
  primaryHref = `${SITE.appUrl}/signup`,
  secondaryLabel = "See pricing",
  secondaryHref = "/pricing",
}: CtaProps) {
  return (
    <section>
      <div className="mx-auto max-w-content px-4 pb-20 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.03] px-6 py-14 text-center shadow-ai backdrop-blur-sm sm:px-12">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-ai-violet/25 blur-3xl"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -bottom-16 -left-16 h-64 w-64 rounded-full bg-ai-cyan/20 blur-3xl"
          />
          <h2 className="relative text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {title}
          </h2>
          <p className="relative mx-auto mt-4 max-w-2xl text-lg text-slate-300">
            {description}
          </p>
          <div className="relative mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href={primaryHref}
              className="inline-flex w-full items-center justify-center rounded-lg bg-ai-gradient px-6 py-3 text-base font-semibold text-white shadow-ai transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-indigo focus-visible:ring-offset-2 focus-visible:ring-offset-[#07070b] sm:w-auto"
            >
              {primaryLabel}
            </a>
            <a
              href={secondaryHref}
              className="inline-flex w-full items-center justify-center rounded-lg border border-white/15 px-6 py-3 text-base font-semibold text-slate-100 transition-colors hover:border-white/25 hover:bg-white/[0.06] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-indigo focus-visible:ring-offset-2 focus-visible:ring-offset-[#07070b] sm:w-auto"
            >
              {secondaryLabel}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
