import FeatureCard from "./FeatureCard";
import RevealGroup from "./motion/RevealGroup";
import RevealItem from "./motion/RevealItem";
import type { Feature } from "@/lib/content";

type FeatureGridProps = {
  features: Feature[];
  detailed?: boolean;
};

/** Responsive grid of feature cards that stagger into view on scroll. */
export default function FeatureGrid({ features, detailed = false }: FeatureGridProps) {
  return (
    <RevealGroup className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3" stagger={0.08}>
      {features.map((feature) => (
        <RevealItem key={feature.id} as="div" className="h-full">
          <FeatureCard feature={feature} detailed={detailed} />
        </RevealItem>
      ))}
    </RevealGroup>
  );
}
