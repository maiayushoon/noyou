import type { ReactNode } from "react";

type SectionHeadingProps = {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  align?: "left" | "center";
  as?: "h1" | "h2" | "h3";
  className?: string;
};

/**
 * Reusable section heading with an optional eyebrow label and description.
 * Keeps heading hierarchy explicit and consistent for accessibility and SEO.
 */
export default function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
  as: Tag = "h2",
  className = "",
}: SectionHeadingProps) {
  const alignment = align === "center" ? "mx-auto text-center" : "text-left";
  return (
    <div className={`max-w-2xl ${alignment} ${className}`}>
      {eyebrow ? (
        <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-amber-200">
          {eyebrow}
        </p>
      ) : null}
      <Tag
        className={`text-balance font-bold tracking-tight text-white ${
          Tag === "h1"
            ? "text-4xl sm:text-5xl"
            : Tag === "h2"
              ? "text-3xl sm:text-4xl"
              : "text-2xl sm:text-3xl"
        }`}
      >
        {title}
      </Tag>
      {description ? (
        <p className="mt-4 text-lg leading-relaxed text-slate-400">{description}</p>
      ) : null}
    </div>
  );
}
