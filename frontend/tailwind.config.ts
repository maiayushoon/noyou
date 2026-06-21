import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      colors: {
        // Dark sidebar surfaces
        sidebar: {
          DEFAULT: "#0f172a",
          deep: "#0b1220",
          hover: "#1e293b",
        },
        canvas: "#12100D",
        // Hairline (also available as a borderColor) — usable as bg-hairline too.
        hairline: "rgba(245,238,228,.09)",
        // AI gradient stops
        ai: {
          indigo: "#C8A24C",
          violet: "#E8D7A8",
          cyan: "#F0E3BE",
        },
        // Band / status semantic colors
        positive: "#10b981",
        neutral: "#64748b",
        negative: "#ef4444",
        warn: "#f59e0b",
      },
      backgroundImage: {
        "ai-gradient":
          "linear-gradient(135deg, #F0DFB0 0%, #D9B86A 48%, #C8A24C 100%)",
        "ai-gradient-soft":
          "linear-gradient(135deg, rgba(240,223,176,.10) 0%, rgba(217,184,106,.10) 48%, rgba(200,162,76,.10) 100%)",
      },
      borderColor: {
        hairline: "rgba(245,238,228,.09)",
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,.4), 0 4px 16px rgba(0,0,0,.3)",
        "card-hover":
          "0 0 0 1px rgba(245,238,228,.06), 0 0 44px -10px rgba(216,184,106,.40)",
        ai: "0 6px 24px rgba(200,162,76,.30)",
      },
      borderRadius: {
        xl: "1rem",
      },
      keyframes: {
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.6s infinite",
      },
    },
  },
  plugins: [],
};

export default config;
