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
      boxShadow: {
        card: "0 1px 2px rgba(15, 27, 43, 0.04), 0 8px 24px rgba(15, 27, 43, 0.06)",
        lift: "0 12px 40px rgba(31, 78, 121, 0.14)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
