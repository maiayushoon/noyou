import { PLANS } from "@/lib/content";

/** Pricing grid rendering all plans, highlighting the featured plan. */
export default function PricingTable() {
  return (
    <div className="grid gap-6 lg:grid-cols-4">
      {PLANS.map((plan) => (
        <div
          key={plan.id}
          className={`relative flex flex-col rounded-2xl border bg-white p-6 shadow-card ${
            plan.featured
              ? "border-brand-600 ring-1 ring-brand-600"
              : "border-slate-200"
          }`}
        >
          {plan.featured ? (
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-600 px-3 py-1 text-xs font-semibold text-white shadow-sm">
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
            className={`mt-5 inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 ${
              plan.featured
                ? "bg-brand-600 text-white hover:bg-brand-700"
                : "border border-slate-300 text-brand-700 hover:border-brand-300 hover:bg-brand-50"
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
      ))}
    </div>
  );
}
