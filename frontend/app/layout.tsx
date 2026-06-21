import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "NoYou — Digital Reputation",
    template: "%s · NoYou",
  },
  description:
    "NoYou monitors, analyzes, and protects your digital reputation across the web and AI engines.",
  applicationName: "NoYou",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#12100D",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-canvas font-sans text-slate-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
