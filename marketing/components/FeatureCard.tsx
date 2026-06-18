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
      className="group flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-card transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lift"
    >
      <div
        aria-hidden="true"
        className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-50 text-2xl"
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
