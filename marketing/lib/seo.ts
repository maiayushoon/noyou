/**
 * lib/seo.ts
 * Metadata helpers and JSON-LD structured-data builders.
 *
 * GEO/AEO note: structured data (JSON-LD) helps AI answer engines and search
 * crawlers understand the entity, its offers, and its FAQs as facts they can
 * cite. Every page exports unique metadata (title/description/canonical) and,
 * where useful, the relevant JSON-LD graph.
 */

import type { Metadata } from "next";
import { SITE, PLANS, FAQS, CURRENCY, type Faq } from "./content";

/** Resolved at build/runtime from the environment; falls back to the brand domain. */
export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL || SITE.domain
).replace(/\/$/, "");

export const ALL_ROUTES = ["/", "/features", "/pricing", "/faq", "/about"] as const;
export type Route = (typeof ALL_ROUTES)[number];

/** Build an absolute URL from a path. */
export function abs(path: string): string {
  if (path.startsWith("http")) return path;
  return `${SITE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}

export const DEFAULT_KEYWORDS = [
  "reputation management",
  "online reputation management",
  "digital identity management",
  "AI reputation monitoring",
  "brand monitoring",
  "personal reputation",
  "reputation score",
  "AEO",
  "GEO",
  "answer engine optimization",
  "generative engine optimization",
  "AI SEO",
  "AI visibility",
  "ChatGPT brand visibility",
  "Perplexity citations",
  "sentiment analysis",
  "mention monitoring",
  "GDPR reputation",
  "executive reputation",
  "founder reputation",
];

type PageMetaInput = {
  title: string;
  description: string;
  path: string;
  keywords?: string[];
  ogType?: "website" | "article";
};

/**
 * Create per-page Metadata with a canonical URL, Open Graph, and Twitter card.
 * The title here is the page-specific part; layout.tsx applies the brand
 * template ("%s | NoYou").
 */
export function pageMetadata({
  title,
  description,
  path,
  keywords,
  ogType = "website",
}: PageMetaInput): Metadata {
  const url = abs(path);
  return {
    title,
    description,
    keywords: keywords ?? DEFAULT_KEYWORDS,
    alternates: { canonical: url },
    openGraph: {
      type: ogType,
      url,
      siteName: SITE.name,
      title: `${title} | ${SITE.name}`,
      description,
      images: [
        {
          url: abs("/opengraph-image"),
          width: 1200,
          height: 630,
          alt: `${SITE.name} — ${SITE.tagline}`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} | ${SITE.name}`,
      description,
      site: SITE.twitter,
      creator: SITE.twitter,
      images: [abs("/opengraph-image")],
    },
  };
}

/* ------------------------------------------------------------------ */
/* JSON-LD builders                                                    */
/* ------------------------------------------------------------------ */

export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": `${SITE_URL}/#organization`,
    name: SITE.name,
    legalName: SITE.legalName,
    url: SITE_URL,
    logo: abs("/icon.svg"),
    description: SITE.description,
    foundingDate: String(SITE.foundedYear),
    email: SITE.email,
    sameAs: [...SITE.sameAs],
    contactPoint: [
      {
        "@type": "ContactPoint",
        contactType: "customer support",
        email: SITE.supportEmail,
        availableLanguage: ["English"],
      },
    ],
  };
}

export function websiteJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${SITE_URL}/#website`,
    name: SITE.name,
    url: SITE_URL,
    description: SITE.shortDescription,
    publisher: { "@id": `${SITE_URL}/#organization` },
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: `${SITE_URL}/faq?q={search_term_string}`,
      },
      "query-input": "required name=search_term_string",
    },
  };
}

/** Organization + WebSite as a single graph, used globally in layout.tsx. */
export function siteGraphJsonLd() {
  return {
    "@context": "https://schema.org",
    "@graph": [organizationJsonLd(), websiteJsonLd()],
  };
}

export function softwareApplicationJsonLd() {
  const offers = PLANS.filter((p) => p.price !== null).map((p) => ({
    "@type": "Offer",
    name: `${SITE.name} ${p.name}`,
    price: String(p.price),
    priceCurrency: CURRENCY,
    category: p.name,
    url: abs("/pricing"),
    availability: "https://schema.org/InStock",
    ...(p.price && p.price > 0
      ? {
          priceSpecification: {
            "@type": "UnitPriceSpecification",
            price: String(p.price),
            priceCurrency: CURRENCY,
            unitText: "MONTH",
            billingDuration: 1,
          },
        }
      : {}),
  }));

  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "@id": `${SITE_URL}/#software`,
    name: SITE.name,
    applicationCategory: "BusinessApplication",
    applicationSubCategory: "Reputation Management Software",
    operatingSystem: "Web",
    url: SITE_URL,
    description: SITE.description,
    offers: {
      "@type": "AggregateOffer",
      priceCurrency: CURRENCY,
      lowPrice: "0",
      highPrice: "59",
      offerCount: String(PLANS.length),
      offers,
    },
    publisher: { "@id": `${SITE_URL}/#organization` },
    featureList: [
      "Web and social media mention monitoring",
      "AI sentiment and risk analysis",
      "0-100 reputation score",
      "High-risk content alerts",
      "Suggested cleanup actions",
      "Pre-Post Check (predictive post risk)",
      "AI Visibility Check across AI answer engines",
    ],
  };
}

export function faqPageJsonLd(faqs: Faq[] = FAQS) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "@id": `${SITE_URL}/faq/#faq`,
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: f.answer,
      },
    })),
  };
}

export type Crumb = { name: string; path: string };

export function breadcrumbJsonLd(crumbs: Crumb[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: crumbs.map((c, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: c.name,
      item: abs(c.path),
    })),
  };
}
