import type { Faq } from "@/lib/content";

type FaqAccordionProps = {
  faqs: Faq[];
};

/**
 * Accessible FAQ list built on the native <details>/<summary> elements.
 * This works without JavaScript, is keyboard-accessible, and renders the full
 * answer text in the HTML so search engines and AI answer engines can read and
 * cite it directly (paired with FAQPage JSON-LD on the page).
 */
export default function FaqAccordion({ faqs }: FaqAccordionProps) {
  return (
    <div className="mx-auto max-w-3xl divide-y divide-white/[0.06] rounded-xl border border-white/[0.06] bg-white/[0.03] backdrop-blur-sm">
      {faqs.map((faq) => (
        <details key={faq.id} id={faq.id} className="group px-6">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-left text-base font-semibold text-slate-100 transition-colors hover:text-white [&::-webkit-details-marker]:hidden">
            <span>{faq.question}</span>
            <svg
              className="h-5 w-5 flex-none text-slate-500 transition-transform group-open:rotate-180"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M5.3 7.3a1 1 0 0 1 1.4 0L10 10.6l3.3-3.3a1 1 0 1 1 1.4 1.4l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 0 1 0-1.4Z"
                clipRule="evenodd"
              />
            </svg>
          </summary>
          <div className="pb-5 text-sm leading-relaxed text-slate-400">
            {faq.answer}
          </div>
        </details>
      ))}
    </div>
  );
}
