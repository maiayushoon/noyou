# NoYou — Marketing Site

The public marketing site for **NoYou**, an AI-powered digital identity and reputation management platform. Built with **Next.js 14 (App Router)**, **TypeScript**, and **Tailwind CSS**, and engineered for **SEO + GEO/AEO** (so AI answer engines like ChatGPT, Perplexity, Gemini, and Google AI Overviews surface and cite the content).

## Tech stack

- Next.js 14.2 (App Router, React Server Components)
- TypeScript (strict)
- Tailwind CSS 3.4
- Zero runtime data dependencies — fully static, server-rendered HTML

## Getting started

```bash
npm install
npm run dev      # http://localhost:3000
```

Build and run the production server:

```bash
npm run build
npm run start
```

## Configuration

The only required environment variable is the canonical site URL, used by
`metadataBase`, the sitemap, robots.txt, JSON-LD, and Open Graph tags.

```bash
# .env.local
NEXT_PUBLIC_SITE_URL=https://noyou.app
```

It defaults to `https://noyou.app` when unset. Copy `.env.example` to
`.env.local` to override (e.g. for a staging domain). **No trailing slash.**

## Project structure

```
marketing/
├─ app/
│  ├─ layout.tsx            # Root layout: global metadata + Organization/WebSite JSON-LD
│  ├─ page.tsx              # Home
│  ├─ features/page.tsx     # Features (Pre-Post Check, AI Visibility, data sources)
│  ├─ pricing/page.tsx      # Pricing (Free/Pro/Premium/Enterprise) + Offer JSON-LD
│  ├─ faq/page.tsx          # FAQ + FAQPage JSON-LD
│  ├─ about/page.tsx        # About, privacy, terms
│  ├─ sitemap.ts            # /sitemap.xml
│  ├─ robots.ts             # /robots.txt
│  ├─ opengraph-image.tsx   # Dynamic 1200x630 OG image
│  ├─ icon.svg              # App icon
│  ├─ favicon.ico
│  └─ globals.css
├─ components/              # Header, Footer, Hero, FeatureCard/Grid, PricingTable,
│                          #   FaqAccordion, Cta, JsonLd, SectionHeading
├─ lib/
│  ├─ content.ts            # All copy/features/pricing/FAQ as typed data
│  └─ seo.ts                # Metadata helpers + JSON-LD builders
└─ public/
   ├─ llms.txt              # llms.txt standard (site summary + page links)
   ├─ llms-full.txt         # Full FAQ answers as markdown for LLM ingestion
   ├─ icon.svg
   ├─ favicon.ico
   └─ site.webmanifest
```

## SEO & GEO/AEO features

- **Server-rendered static HTML** — every page is crawlable without JavaScript.
- **Per-page metadata** — unique title, description, and canonical URL via the
  Next.js Metadata API; a title template (`%s | NoYou`).
- **Open Graph + Twitter cards** with a dynamically generated image.
- **JSON-LD structured data**: `Organization`, `WebSite` + `SearchAction`
  (global), `SoftwareApplication` with `Offer`/`AggregateOffer`, `FAQPage`, and
  `BreadcrumbList`.
- **robots.txt** (allows all crawlers, incl. AI bots) and a dynamic
  **sitemap.xml**.
- **llms.txt** and **llms-full.txt** — the emerging standard that tells LLMs
  what the site is and links the key pages; the `-full` file includes complete
  FAQ answers as markdown.
- **Semantic, accessible HTML** — proper heading hierarchy, a skip link, native
  `<details>` FAQ accordion, reduced-motion support, focus-visible styles.
- **Fast Core Web Vitals** — self-hosted Inter via `next/font`, no client JS for
  content, Tailwind's minimal CSS.

## Deploying on Vercel

1. Push this `marketing/` directory to a Git repository.
2. In Vercel, **New Project** → import the repo. If this is a subdirectory of a
   monorepo, set the **Root Directory** to `marketing`.
3. Framework preset: **Next.js** (auto-detected). Build command `next build`,
   output handled automatically.
4. Add an environment variable: `NEXT_PUBLIC_SITE_URL` =
   `https://noyou.app` (or your domain).
5. Deploy. Add your custom domain under **Settings → Domains**.

Any Node host that supports Next.js 14 works too: run `npm run build` then
`npm run start` (defaults to port 3000).

## License

© NoYou, Inc. All rights reserved.
