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
          indigo: "#C8A24C",
          violet: "#E8D7A8",
          cyan: "#F0E3BE",
        },
        // Brand ramp repointed navy -> warm gold (dark 950 .. pale 50).
        brand: {
          DEFAULT: "#C8A24C",
          50: "#FAF4E4",
          100: "#F4E8C9",
          200: "#EAD6A2",
          300: "#E0C57C",
          400: "#D9B86A",
          500: "#C8A24C",
          600: "#A9853A",
          700: "#86692E",
          800: "#5F4B22",
          900: "#3C3017",
          950: "#241D0E",
        },
        // Accent ramp repointed teal -> champagne/gold.
        accent: {
          DEFAULT: "#D9B86A",
          50: "#FBF6E8",
          100: "#F6ECCF",
          200: "#F0E3BE",
          300: "#E8D7A8",
          400: "#DFC68A",
          500: "#D9B86A",
          600: "#C8A24C",
          700: "#A9853A",
          800: "#86692E",
          900: "#5F4B22",
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
        xl: "1rem",
        "2xl": "1.25rem",
      },
      backgroundImage: {
        // Signature brand gradient: champagne -> gold.
        "ai-gradient":
          "linear-gradient(135deg, #F0DFB0 0%, #D9B86A 48%, #C8A24C 100%)",
        "ai-gradient-soft":
          "linear-gradient(135deg, rgba(240,223,176,0.10) 0%, rgba(217,184,106,0.10) 48%, rgba(200,162,76,0.10) 100%)",
        // Very subtle warm gold radial glow washes for deep, warm charcoal depth.
        "ai-radial":
          "radial-gradient(60rem 40rem at 50% -10%, rgba(200,162,76,0.06), transparent 60%), radial-gradient(50rem 36rem at 100% 0%, rgba(200,162,76,0.06), transparent 55%)",
      },
      boxShadow: {
        card: "0 1px 2px rgba(0, 0, 0, 0.4), 0 8px 24px rgba(0, 0, 0, 0.35)",
        lift: "0 12px 40px rgba(0, 0, 0, 0.45)",
        // Glowing gold halo for the 3D centerpiece and gradient buttons.
        ai: "0 18px 60px -12px rgba(200, 162, 76, 0.40), 0 8px 24px -8px rgba(216, 184, 106, 0.30)",
        // Soft gold glow used on hover for sleek glass surfaces.
        "ai-glow": "0 0 44px -10px rgba(216, 184, 106, 0.40)",
        hairline: "0 0 0 1px rgba(245, 238, 228, 0.09)",
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
