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
    <section className="bg-white">
      <div className="mx-auto max-w-content px-4 pb-20 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-2xl bg-brand-700 px-6 py-14 text-center shadow-lift sm:px-12">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-accent-500/20 blur-3xl"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -bottom-16 -left-16 h-64 w-64 rounded-full bg-brand-400/20 blur-3xl"
          />
          <h2 className="relative text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {title}
          </h2>
          <p className="relative mx-auto mt-4 max-w-2xl text-lg text-brand-100">
            {description}
          </p>
          <div className="relative mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href={primaryHref}
              className="inline-flex w-full items-center justify-center rounded-lg bg-white px-6 py-3 text-base font-semibold text-brand-700 shadow-sm transition-colors hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white sm:w-auto"
            >
              {primaryLabel}
            </a>
            <a
              href={secondaryHref}
              className="inline-flex w-full items-center justify-center rounded-lg border border-white/30 px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white sm:w-auto"
            >
              {secondaryLabel}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
