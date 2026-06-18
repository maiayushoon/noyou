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
        canvas: "#f8fafc",
        // AI gradient stops
        ai: {
          indigo: "#6366f1",
          violet: "#8b5cf6",
          cyan: "#22d3ee",
        },
        // Band / status semantic colors
        positive: "#10b981",
        neutral: "#64748b",
        negative: "#ef4444",
        warn: "#f59e0b",
      },
      backgroundImage: {
        "ai-gradient":
          "linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #22d3ee 100%)",
        "ai-gradient-soft":
          "linear-gradient(135deg, rgba(99,102,241,.12) 0%, rgba(139,92,246,.12) 50%, rgba(34,211,238,.12) 100%)",
      },
      borderColor: {
        hairline: "rgba(15,23,42,.07)",
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,23,42,.04), 0 4px 16px rgba(15,23,42,.05)",
        "card-hover": "0 2px 4px rgba(15,23,42,.06), 0 12px 28px rgba(15,23,42,.08)",
        ai: "0 6px 24px rgba(99,102,241,.28)",
      },
      borderRadius: {
        xl: "0.875rem",
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
