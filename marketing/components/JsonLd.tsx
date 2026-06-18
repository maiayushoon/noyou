/**
 * JsonLd
 * Renders a <script type="application/ld+json"> tag with structured data.
 * This is a server component (no client JS needed) — the script ships in the
 * initial HTML so crawlers and AI answer engines read it without executing JS.
 */
type JsonLdProps = {
  data: Record<string, unknown> | Record<string, unknown>[];
  id?: string;
};

export default function JsonLd({ data, id }: JsonLdProps) {
  return (
    <script
      type="application/ld+json"
      id={id}
      // JSON.stringify output is safe to embed; we escape the closing-script
      // sequence defensively in case any copy ever contains it.
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
