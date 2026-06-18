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
          background: "linear-gradient(135deg, #163653 0%, #1f4e79 60%, #2f6aa8 100%)",
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
              background: "white",
              color: "#1f4e79",
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
              color: "#aec9e7",
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
            color: "#d6e4f3",
          }}
        >
          <div
            style={{
              width: "14px",
              height: "14px",
              borderRadius: "9999px",
              background: "#16b8a6",
            }}
          />
          noyou.app
        </div>
      </div>
    ),
    { ...size },
  );
}
