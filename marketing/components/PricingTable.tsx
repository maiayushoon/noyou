import { PLANS } from "@/lib/content";
import RevealGroup from "./motion/RevealGroup";
import RevealItem from "./motion/RevealItem";

/** Pricing grid rendering all plans, highlighting the featured plan. */
export default function PricingTable() {
  return (
    <RevealGroup className="grid gap-6 lg:grid-cols-4" stagger={0.08}>
      {PLANS.map((plan) => (
        <RevealItem key={plan.id} as="div" className="h-full">
          <div
            className={`relative flex h-full flex-col rounded-2xl border bg-white p-6 transition-all duration-300 hover:-translate-y-1 ${
              plan.featured
                ? "border-indigo-200 shadow-ai ring-1 ring-indigo-200"
                : "border-slate-200 shadow-card hover:border-indigo-200 hover:shadow-ai"
            }`}
          >
            {plan.featured ? (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-ai-gradient px-3 py-1 text-xs font-semibold text-white shadow-ai">
                Most popular
              </span>
            ) : null}

            <h3 className="text-lg font-semibold text-brand-900">{plan.name}</h3>

            <div className="mt-3 flex items-baseline gap-1">
              <span className="text-4xl font-bold tracking-tight text-brand-900">
                {plan.priceLabel}
              </span>
              <span className="text-sm text-slate-500">/{plan.period}</span>
            </div>

            <p className="mt-3 min-h-[3rem] text-sm leading-relaxed text-slate-600">
              {plan.blurb}
            </p>

            <a
              href={plan.cta.href}
              className={`mt-5 inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
                plan.featured
                  ? "bg-ai-gradient text-white shadow-ai hover:-translate-y-0.5 focus-visible:ring-indigo-500"
                  : "border border-slate-300 text-brand-700 hover:border-indigo-300 hover:bg-indigo-50 focus-visible:ring-brand-500"
              }`}
            >
              {plan.cta.label}
            </a>

            <ul className="mt-6 space-y-3 text-sm">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2 text-slate-700">
                  <svg
                    className="mt-0.5 h-4 w-4 flex-none text-accent-600"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.7 5.3a1 1 0 0 1 0 1.4l-7.5 7.5a1 1 0 0 1-1.4 0L3.3 9.7a1 1 0 1 1 1.4-1.4l3.3 3.29 6.8-6.8a1 1 0 0 1 1.4 0Z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </RevealItem>
      ))}
    </RevealGroup>
  );
}
