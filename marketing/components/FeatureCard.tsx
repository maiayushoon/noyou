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
      className="group relative flex h-full flex-col overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.03] p-6 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.12] hover:shadow-ai-glow"
    >
      {/* Gradient accent that fades in on hover. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-ai-gradient opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      />
      <div
        aria-hidden="true"
        className="flex h-11 w-11 items-center justify-center rounded-xl bg-ai-gradient-soft text-2xl ring-1 ring-white/10 transition-transform duration-300 group-hover:scale-105"
      >
        {feature.icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-white">
        {feature.title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">
        {detailed ? feature.details : feature.summary}
      </p>
    </article>
  );
}
