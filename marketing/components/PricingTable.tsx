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
            className={`relative flex h-full flex-col rounded-xl border bg-white/[0.03] p-6 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 ${
              plan.featured
                ? "border-ai-violet/40 shadow-ai ring-1 ring-ai-violet/30"
                : "border-white/[0.06] hover:border-white/[0.12] hover:shadow-ai-glow"
            }`}
          >
            {plan.featured ? (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-ai-gradient px-3 py-1 text-xs font-semibold text-white shadow-ai">
                Most popular
              </span>
            ) : null}

            <h3 className="text-lg font-semibold text-white">{plan.name}</h3>

            <div className="mt-3 flex items-baseline gap-1">
              <span className="text-4xl font-bold tracking-tight text-white">
                {plan.priceLabel}
              </span>
              <span className="text-sm text-slate-500">/{plan.period}</span>
            </div>

            <p className="mt-3 min-h-[3rem] text-sm leading-relaxed text-slate-400">
              {plan.blurb}
            </p>

            <a
              href={plan.cta.href}
              className={`mt-5 inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#07070b] ${
                plan.featured
                  ? "bg-ai-gradient text-white shadow-ai hover:-translate-y-0.5 focus-visible:ring-ai-indigo"
                  : "border border-white/10 text-slate-100 hover:border-white/20 hover:bg-white/[0.06] focus-visible:ring-ai-indigo"
              }`}
            >
              {plan.cta.label}
            </a>

            <ul className="mt-6 space-y-3 text-sm">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2 text-slate-300">
                  <svg
                    className="mt-0.5 h-4 w-4 flex-none text-emerald-400"
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
