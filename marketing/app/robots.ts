import type { MetadataRoute } from "next";
import { SITE_URL, abs } from "@/lib/seo";

/**
 * robots.txt — allow all crawlers (including AI answer-engine crawlers such as
 * GPTBot, PerplexityBot, Google-Extended, and ClaudeBot) and point them to the
 * sitemap. Served by Next.js at /robots.txt.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
      },
    ],
    sitemap: abs("/sitemap.xml"),
    host: SITE_URL,
  };
}
