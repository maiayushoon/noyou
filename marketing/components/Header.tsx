import Link from "next/link";
import { NAV_LINKS, SITE } from "@/lib/content";

/**
 * Site header with primary navigation and a "Sign in" action that links to the
 * web app. Uses a <details> element for the mobile menu so it works without any
 * client-side JavaScript (progressive enhancement, fully crawlable).
 */
export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/70 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/70">
      <div className="mx-auto flex h-16 max-w-content items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex items-center gap-2 rounded-md font-bold text-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          aria-label={`${SITE.name} home`}
        >
          <span
            aria-hidden="true"
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-black text-white"
          >
            N
          </span>
          <span className="text-lg tracking-tight">{SITE.name}</span>
        </Link>

        {/* Desktop nav */}
        <nav
          aria-label="Primary"
          className="hidden items-center gap-8 md:flex"
        >
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-slate-700 transition-colors hover:text-brand-700"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <a
            href={SITE.appUrl}
            className="text-sm font-medium text-slate-700 transition-colors hover:text-brand-700"
          >
            Sign in
          </a>
          <a
            href={`${SITE.appUrl}/signup`}
            className="inline-flex items-center justify-center rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
          >
            Get started
          </a>
        </div>

        {/* Mobile menu (no-JS friendly) */}
        <details className="relative md:hidden">
          <summary
            className="flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-lg border border-slate-200 text-slate-700 [&::-webkit-details-marker]:hidden"
            aria-label="Toggle menu"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </summary>
          <div className="absolute right-0 mt-2 w-56 rounded-xl border border-slate-200 bg-white p-2 shadow-lift">
            <nav aria-label="Mobile" className="flex flex-col">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-brand-700"
                >
                  {link.label}
                </Link>
              ))}
              <div className="my-2 h-px bg-slate-100" />
              <a
                href={SITE.appUrl}
                className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Sign in
              </a>
              <a
                href={`${SITE.appUrl}/signup`}
                className="mt-1 rounded-lg bg-brand-600 px-3 py-2 text-center text-sm font-semibold text-white hover:bg-brand-700"
              >
                Get started
              </a>
            </nav>
          </div>
        </details>
      </div>
    </header>
  );
}
