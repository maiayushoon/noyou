import type { MetadataRoute } from "next";
import { ALL_ROUTES, abs } from "@/lib/seo";

/**
 * Dynamic sitemap covering every route. Next.js serves this at /sitemap.xml.
 * Home gets the highest priority; supporting pages are weighted below it.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();

  const priorities: Record<string, number> = {
    "/": 1,
    "/features": 0.9,
    "/pricing": 0.9,
    "/faq": 0.8,
    "/about": 0.6,
  };

  return ALL_ROUTES.map((route) => ({
    url: abs(route),
    lastModified,
    changeFrequency: route === "/" ? "weekly" : "monthly",
    priority: priorities[route] ?? 0.5,
  }));
}
