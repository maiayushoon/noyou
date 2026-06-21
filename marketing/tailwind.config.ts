import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Direct, single-token references to the brand gradient stops so dark
        // surfaces can lean on the ai-* accent palette (focus rings, glows).
        ai: {
          indigo: "#6366f1",
          violet: "#8b5cf6",
          cyan: "#22d3ee",
        },
        brand: {
          DEFAULT: "#1f4e79",
          50: "#eef4fb",
          100: "#d6e4f3",
          200: "#aec9e7",
          300: "#7ea9d6",
          400: "#4f87c2",
          500: "#2f6aa8",
          600: "#1f4e79",
          700: "#1a4366",
          800: "#163653",
          900: "#122b43",
          950: "#0b1b2b",
        },
        accent: {
          DEFAULT: "#16b8a6",
          50: "#effcf9",
          100: "#c9f6ee",
          200: "#96ecde",
          300: "#5cdac9",
          400: "#2fc2b2",
          500: "#16b8a6",
          600: "#0d8b80",
          700: "#107068",
          800: "#125954",
          900: "#134a47",
        },
      },
      fontFamily: {
        sans: [
          "var(--font-inter)",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      maxWidth: {
        content: "72rem",
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.25rem",
      },
      backgroundImage: {
        // Signature AI brand gradient: indigo -> violet -> cyan.
        "ai-gradient":
          "linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #22d3ee 100%)",
        "ai-gradient-soft":
          "linear-gradient(135deg, rgba(99,102,241,0.22) 0%, rgba(139,92,246,0.18) 50%, rgba(34,211,238,0.22) 100%)",
        // Very subtle radial glow washes for deep, near-black page depth.
        "ai-radial":
          "radial-gradient(60rem 40rem at 50% -10%, rgba(99,102,241,0.10), transparent 60%), radial-gradient(50rem 36rem at 100% 0%, rgba(34,211,238,0.06), transparent 55%)",
      },
      boxShadow: {
        card: "0 1px 2px rgba(0, 0, 0, 0.4), 0 8px 24px rgba(0, 0, 0, 0.35)",
        lift: "0 12px 40px rgba(0, 0, 0, 0.45)",
        // Glowing halo for the 3D centerpiece and gradient buttons.
        ai: "0 18px 60px -12px rgba(99, 102, 241, 0.55), 0 8px 24px -8px rgba(34, 211, 238, 0.4)",
        // Soft accent glow used on hover for sleek glass surfaces.
        "ai-glow": "0 0 40px -8px rgba(139, 92, 246, 0.45)",
        hairline: "0 0 0 1px rgba(255, 255, 255, 0.08)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "float-slow": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-16px)" },
        },
        "spin-slow": {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "0.85" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out both",
        float: "float 6s ease-in-out infinite",
        "float-slow": "float-slow 9s ease-in-out infinite",
        "spin-slow": "spin-slow 26s linear infinite",
        "pulse-soft": "pulse-soft 5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
