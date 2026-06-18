import { SITE, STATS, TRUST_LINE } from "@/lib/content";

/**
 * Home-page hero. The H1 states the product category and benefit in plain
 * language so both readers and AI answer engines get a direct, citable answer
 * to "what is NoYou?".
 */
export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-brand-50 via-white to-white">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 -top-40 flex justify-center"
      >
        <div className="h-72 w-[40rem] rounded-full bg-accent-200/30 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-content px-4 pb-16 pt-16 sm:px-6 sm:pt-20 lg:px-8 lg:pt-24">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-white px-3 py-1 text-xs font-semibold text-brand-700 shadow-sm">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
            New: AI Visibility Check for ChatGPT, Perplexity & Gemini
          </span>

          <h1 className="mt-6 text-balance text-4xl font-bold tracking-tight text-brand-900 sm:text-5xl lg:text-6xl">
            Own your online and{" "}
            <span className="text-brand-600">AI reputation</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-balance text-lg leading-relaxed text-slate-600 sm:text-xl">
            {SITE.name} is an AI-powered digital identity and reputation manager.
            It monitors the web and social for mentions of you, scores your
            reputation 0-100, flags high-risk content, and shows you how AI
            engines describe your brand.
          </p>

          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href={`${SITE.appUrl}/signup`}
              className="inline-flex w-full items-center justify-center rounded-lg bg-brand-600 px-6 py-3 text-base font-semibold text-white shadow-sm transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 sm:w-auto"
            >
              Start free — no card required
            </a>
            <a
              href="/features"
              className="inline-flex w-full items-center justify-center rounded-lg border border-slate-300 bg-white px-6 py-3 text-base font-semibold text-slate-800 transition-colors hover:border-brand-300 hover:text-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 sm:w-auto"
            >
              See how it works
            </a>
          </div>

          <p className="mx-auto mt-6 max-w-2xl text-sm text-slate-500">
            {TRUST_LINE}
          </p>
        </div>

        {/* Stat band */}
        <dl className="mx-auto mt-14 grid max-w-4xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-slate-200 bg-slate-200 shadow-card sm:grid-cols-4">
          {STATS.map((stat) => (
            <div key={stat.label} className="bg-white p-5 text-center">
              <dt className="sr-only">{stat.label}</dt>
              <dd>
                <span className="block text-2xl font-bold text-brand-700">
                  {stat.value}
                </span>
                <span className="mt-1 block text-xs leading-snug text-slate-500">
                  {stat.label}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
