import { ImageResponse } from "next/og";
import { SITE } from "@/lib/content";

/**
 * Dynamically generated 1200x630 Open Graph / Twitter card image.
 * Next.js serves this at /opengraph-image. Uses the Edge runtime and core
 * system fonts so no font files are required at build time.
 */
export const runtime = "edge";
export const alt = `${SITE.name} — ${SITE.tagline}`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px",
          background: "linear-gradient(135deg, #0b0b14 0%, #07070b 55%, #0d0b18 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "72px",
              height: "72px",
              borderRadius: "18px",
              background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #22d3ee 100%)",
              color: "white",
              fontSize: "44px",
              fontWeight: 800,
            }}
          >
            N
          </div>
          <div style={{ fontSize: "40px", fontWeight: 700 }}>{SITE.name}</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <div
            style={{
              fontSize: "68px",
              fontWeight: 800,
              lineHeight: 1.05,
              maxWidth: "920px",
            }}
          >
            Own your online and AI reputation
          </div>
          <div
            style={{
              fontSize: "30px",
              color: "#94a3b8",
              maxWidth: "880px",
              lineHeight: 1.3,
            }}
          >
            AI-powered monitoring, a 0-100 reputation score, risk alerts, and AI
            visibility — all in one place.
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            fontSize: "26px",
            color: "#cbd5e1",
          }}
        >
          <div
            style={{
              width: "14px",
              height: "14px",
              borderRadius: "9999px",
              background: "#22d3ee",
            }}
          />
          noyou.app
        </div>
      </div>
    ),
    { ...size },
  );
}
