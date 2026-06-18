import FeatureCard from "./FeatureCard";
import type { Feature } from "@/lib/content";

type FeatureGridProps = {
  features: Feature[];
  detailed?: boolean;
};

/** Responsive grid of feature cards. */
export default function FeatureGrid({ features, detailed = false }: FeatureGridProps) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {features.map((feature) => (
        <FeatureCard key={feature.id} feature={feature} detailed={detailed} />
      ))}
    </div>
  );
}
