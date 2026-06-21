import type { Feature } from "@/lib/content";

type FeatureCardProps = {
  feature: Feature;
  /** When true, renders the longer `details` copy instead of the `summary`. */
  detailed?: boolean;
};

/** A single feature tile. Used in the home grid and the features page. */
export default function FeatureCard({ feature, detailed = false }: FeatureCardProps) {
  return (
    <article
      id={feature.id}
      className="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-card transition-all duration-300 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-ai"
    >
      {/* Gradient accent that fades in on hover. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-ai-gradient opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      />
      <div
        aria-hidden="true"
        className="flex h-11 w-11 items-center justify-center rounded-xl bg-ai-gradient-soft text-2xl ring-1 ring-indigo-100 transition-transform duration-300 group-hover:scale-105"
      >
        {feature.icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-brand-900">
        {feature.title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">
        {detailed ? feature.details : feature.summary}
      </p>
    </article>
  );
}
