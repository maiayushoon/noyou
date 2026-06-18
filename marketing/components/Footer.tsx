import Link from "next/link";
import {
  FOOTER_LINKS,
  FOOTER_LEGAL,
  SITE,
} from "@/lib/content";

/** Site footer with grouped navigation, legal links, and a brand summary. */
export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-content px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-5">
          <div className="col-span-2">
            <Link
              href="/"
              className="flex items-center gap-2 font-bold text-brand-700"
            >
              <span
                aria-hidden="true"
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-black text-white"
              >
                N
              </span>
              <span className="text-lg tracking-tight">{SITE.name}</span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-slate-600">
              {SITE.shortDescription}
            </p>
            <a
              href={`mailto:${SITE.email}`}
              className="mt-4 inline-block text-sm font-medium text-brand-700 hover:text-brand-800"
            >
              {SITE.email}
            </a>
          </div>

          {FOOTER_LINKS.map((group) => (
            <div key={group.heading}>
              <h2 className="text-sm font-semibold text-brand-900">
                {group.heading}
              </h2>
              <ul className="mt-3 space-y-2">
                {group.links.map((link) => (
                  <li key={`${group.heading}-${link.href}`}>
                    {link.href.startsWith("/") ? (
                      <Link
                        href={link.href}
                        className="text-sm text-slate-600 hover:text-brand-700"
                      >
                        {link.label}
                      </Link>
                    ) : (
                      <a
                        href={link.href}
                        className="text-sm text-slate-600 hover:text-brand-700"
                      >
                        {link.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-4 border-t border-slate-200 pt-6 sm:flex-row sm:items-center">
          <p className="text-sm text-slate-500">
            © {year} {SITE.legalName}. All rights reserved.
          </p>
          <ul className="flex flex-wrap gap-x-6 gap-y-2">
            {FOOTER_LEGAL.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-sm text-slate-500 hover:text-brand-700"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </footer>
  );
}
