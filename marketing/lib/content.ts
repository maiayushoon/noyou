/**
 * lib/content.ts
 * Single source of truth for all marketing copy, presented as typed data.
 * Keeping copy here (rather than inline in JSX) makes it reusable across pages,
 * the sitemap, the llms.txt files, and JSON-LD structured data.
 */

export const SITE = {
  name: "NoYou",
  legalName: "NoYou, Inc.",
  domain: "https://noyou.app",
  appUrl: "https://app.noyou.app",
  tagline: "Own your online and AI reputation.",
  description:
    "NoYou is an AI-powered digital identity and reputation management platform. It monitors the web and social media for mentions of you or your brand, runs AI sentiment and risk analysis on every result, computes a 0-100 reputation score, alerts you to high-risk content, and recommends cleanup actions.",
  shortDescription:
    "AI-powered digital identity and reputation management — monitor mentions, score your reputation, catch risks, and shape how AI engines describe you.",
  email: "hello@noyou.app",
  supportEmail: "support@noyou.app",
  foundedYear: 2024,
  twitter: "@noyouapp",
  sameAs: [
    "https://twitter.com/noyouapp",
    "https://www.linkedin.com/company/noyou",
    "https://github.com/noyou",
  ],
} as const;

export type NavLink = { label: string; href: string };

export const NAV_LINKS: NavLink[] = [
  { label: "Features", href: "/features" },
  { label: "Pricing", href: "/pricing" },
  { label: "FAQ", href: "/faq" },
  { label: "About", href: "/about" },
];

export const FOOTER_LINKS: { heading: string; links: NavLink[] }[] = [
  {
    heading: "Product",
    links: [
      { label: "Features", href: "/features" },
      { label: "Pricing", href: "/pricing" },
      { label: "AI Visibility Check", href: "/features#ai-visibility" },
      { label: "Pre-Post Check", href: "/features#pre-post-check" },
    ],
  },
  {
    heading: "Company",
    links: [
      { label: "About", href: "/about" },
      { label: "FAQ", href: "/faq" },
      { label: "Sign in", href: SITE.appUrl },
    ],
  },
  {
    heading: "Resources",
    links: [
      { label: "llms.txt", href: "/llms.txt" },
      { label: "Sitemap", href: "/sitemap.xml" },
      { label: "Contact", href: `mailto:${SITE.email}` },
    ],
  },
];

export const FOOTER_LEGAL: NavLink[] = [
  { label: "Privacy", href: "/about#privacy" },
  { label: "Terms", href: "/about#terms" },
  { label: "GDPR / CCPA", href: "/faq#privacy" },
];

/* ------------------------------------------------------------------ */
/* Social proof / trust stats                                          */
/* ------------------------------------------------------------------ */

export const STATS: { value: string; label: string }[] = [
  { value: "0-100", label: "Reputation score, updated continuously" },
  { value: "6+", label: "Web & social sources scanned per run" },
  { value: "< 60s", label: "From scan to AI risk analysis" },
  { value: "4", label: "AI answer engines checked for visibility" },
];

export const TRUST_LINE =
  "Built for founders, executives, professionals, and brands who need to control how they look online — and how AI describes them.";

/* ------------------------------------------------------------------ */
/* Features                                                            */
/* ------------------------------------------------------------------ */

export type Feature = {
  id: string;
  icon: string; // emoji used as a lightweight, dependency-free icon
  title: string;
  summary: string;
  details: string;
};

export const FEATURES: Feature[] = [
  {
    id: "monitoring",
    icon: "🔎",
    title: "Web & social monitoring",
    summary:
      "Continuously scans the open web and social platforms for new mentions of your name, brand, or company.",
    details:
      "NoYou queries real, keyless sources — DuckDuckGo, Hacker News, and Reddit — out of the box, with no API keys required. Add Google Custom Search (CSE) and large language models when you want deeper coverage. Every scan is relevance-filtered, so you see mentions that are actually about you, not noise.",
  },
  {
    id: "sentiment",
    icon: "🧠",
    title: "AI sentiment & risk analysis",
    summary:
      "Each mention is analyzed for sentiment and risk so you instantly know what's positive, neutral, or damaging.",
    details:
      "NoYou classifies every mention as positive, neutral, or negative and assigns a risk level. High-risk content — defamation, leaks, impersonation, viral complaints — is flagged so you can act before it spreads, rather than discovering it weeks later.",
  },
  {
    id: "score",
    icon: "📊",
    title: "0-100 reputation score",
    summary:
      "A single, continuously updated number that summarizes your overall standing across everything we find.",
    details:
      "The reputation score weighs the volume, sentiment, risk, recency, and reach of mentions into one 0-100 figure. Track it over time to see whether your reputation is improving or slipping, and to measure the impact of cleanup work.",
  },
  {
    id: "alerts",
    icon: "🚨",
    title: "High-risk alerts",
    summary:
      "Get notified the moment NoYou detects content that could hurt you, so nothing festers unnoticed.",
    details:
      "Alerts trigger on high-risk mentions and on sudden drops in your score. You decide what counts as urgent. Early warning turns a potential crisis into a manageable task.",
  },
  {
    id: "cleanup",
    icon: "🧹",
    title: "Suggested cleanup actions",
    summary:
      "For every risk, NoYou recommends concrete next steps — from outreach templates to suppression tactics.",
    details:
      "Instead of leaving you to figure out what to do, NoYou suggests practical actions: request removal, respond publicly, push positive content to bury negatives, or escalate. Each suggestion is matched to the type and severity of the issue.",
  },
  {
    id: "pre-post-check",
    icon: "🛡️",
    title: "Pre-Post Check (predictive)",
    summary:
      "Paste a draft post and NoYou predicts whether it could hurt your reputation before you publish it.",
    details:
      "Pre-Post Check is a predictive safeguard. Drop in a tweet, comment, or announcement and NoYou estimates its reputational risk, flags wording that could be misread, and suggests safer phrasing — so you catch the bad post before the internet does.",
  },
  {
    id: "ai-visibility",
    icon: "🤖",
    title: "AI Visibility Check",
    summary:
      "See how ChatGPT, Perplexity, Gemini, and Google AI Overviews describe you — and fix what's wrong.",
    details:
      "AI answer engines now shape first impressions. The AI Visibility Check asks the major engines how they describe your brand, surfaces inaccuracies and outdated claims, and recommends content to publish so AI tools cite the right facts about you.",
  },
  {
    id: "private",
    icon: "🔒",
    title: "Private & compliant",
    summary:
      "NoYou runs on public data, supports GDPR/CCPA requests, and can run fully offline for sensitive use.",
    details:
      "We analyze publicly available mentions. You can export or delete your data at any time, and the scanning engine can run entirely offline with keyless sources — useful for privacy-sensitive teams and air-gapped environments.",
  },
];

/* ------------------------------------------------------------------ */
/* How it works                                                        */
/* ------------------------------------------------------------------ */

export type Step = { number: number; title: string; description: string };

export const HOW_IT_WORKS: Step[] = [
  {
    number: 1,
    title: "Tell NoYou who to watch",
    description:
      "Add your name, brand, company, or handles. NoYou builds a relevance-filtered watch list so scans stay focused on you.",
  },
  {
    number: 2,
    title: "We scan the web & social",
    description:
      "NoYou pulls fresh mentions from DuckDuckGo, Hacker News, Reddit, and optional Google CSE — no API keys needed to get started.",
  },
  {
    number: 3,
    title: "AI scores every mention",
    description:
      "Each result is run through AI sentiment and risk analysis, then rolled up into your single 0-100 reputation score.",
  },
  {
    number: 4,
    title: "You act with confidence",
    description:
      "Review alerts, follow suggested cleanup actions, run a Pre-Post Check before publishing, and verify how AI engines describe you.",
  },
];

/* ------------------------------------------------------------------ */
/* Data sources                                                        */
/* ------------------------------------------------------------------ */

export const DATA_SOURCES: { name: string; type: string; keyless: boolean }[] = [
  { name: "DuckDuckGo", type: "Web search", keyless: true },
  { name: "Hacker News", type: "Tech community", keyless: true },
  { name: "Reddit", type: "Social discussion", keyless: true },
  { name: "Google Custom Search (CSE)", type: "Web search", keyless: false },
  { name: "LLM providers", type: "AI analysis & visibility", keyless: false },
];

/* ------------------------------------------------------------------ */
/* Pricing                                                             */
/* ------------------------------------------------------------------ */

export type Plan = {
  id: string;
  name: string;
  price: number | null; // null => custom (Enterprise)
  priceLabel: string;
  period: string;
  blurb: string;
  features: string[];
  cta: { label: string; href: string };
  featured?: boolean;
};

export const CURRENCY = "USD" as const;

export const PLANS: Plan[] = [
  {
    id: "free",
    name: "Free",
    price: 0,
    priceLabel: "$0",
    period: "forever",
    blurb: "Check your reputation and try AI risk analysis with keyless sources.",
    features: [
      "1 monitored identity",
      "Weekly web & social scan",
      "Keyless sources (DuckDuckGo, Hacker News, Reddit)",
      "0-100 reputation score",
      "Basic sentiment analysis",
      "3 Pre-Post Checks / month",
    ],
    cta: { label: "Start free", href: `${SITE.appUrl}/signup` },
  },
  {
    id: "pro",
    name: "Pro",
    price: 29,
    priceLabel: "$29",
    period: "per month",
    blurb: "For professionals and founders actively managing their reputation.",
    features: [
      "3 monitored identities",
      "Daily scans across all sources",
      "Full AI sentiment & risk analysis",
      "High-risk alerts (email)",
      "Suggested cleanup actions",
      "Unlimited Pre-Post Checks",
      "AI Visibility Check (monthly)",
    ],
    cta: { label: "Start Pro", href: `${SITE.appUrl}/signup?plan=pro` },
    featured: true,
  },
  {
    id: "premium",
    name: "Premium",
    price: 59,
    priceLabel: "$59",
    period: "per month",
    blurb: "For executives and brands who need deeper coverage and faster response.",
    features: [
      "10 monitored identities",
      "Hourly scans + priority queue",
      "Real-time high-risk alerts",
      "AI Visibility Check (weekly)",
      "Google CSE + LLM integrations",
      "Historical score trends & exports",
      "Priority support",
    ],
    cta: { label: "Start Premium", href: `${SITE.appUrl}/signup?plan=premium` },
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: null,
    priceLabel: "Custom",
    period: "contact us",
    blurb: "For teams, agencies, and organizations with custom needs.",
    features: [
      "Unlimited identities & seats",
      "On-prem / offline deployment option",
      "SSO, audit logs, and roles",
      "Custom data sources & integrations",
      "Dedicated success manager",
      "SLA & custom data residency",
    ],
    cta: { label: "Contact sales", href: `mailto:${SITE.email}?subject=Enterprise` },
  },
];

/* ------------------------------------------------------------------ */
/* FAQ — real Q&A, used for content + FAQPage JSON-LD + llms-full.txt  */
/* ------------------------------------------------------------------ */

export type Faq = { id: string; question: string; answer: string };

export const FAQS: Faq[] = [
  {
    id: "what-is-noyou",
    question: "What is NoYou?",
    answer:
      "NoYou is an AI-powered digital identity and reputation management platform. It continuously monitors the web and social media for mentions of a person or brand, runs AI sentiment and risk analysis on each mention, computes a single 0-100 reputation score, raises alerts on high-risk content, and suggests cleanup actions. It also offers a predictive Pre-Post Check that estimates whether a draft post could hurt you, and an AI Visibility Check that shows how AI answer engines describe your brand.",
  },
  {
    id: "how-it-works",
    question: "How does NoYou work?",
    answer:
      "You tell NoYou who to watch — your name, brand, company, or handles. NoYou then scans real sources (DuckDuckGo, Hacker News, and Reddit work with no API keys; Google Custom Search and LLM providers plug in for deeper coverage). Each mention is relevance-filtered, then analyzed by AI for sentiment and risk. Results roll up into a 0-100 reputation score. When NoYou finds high-risk content, it alerts you and recommends concrete next steps.",
  },
  {
    id: "what-is-aeo-geo",
    question: "What is AEO / GEO (AI SEO), and why does it matter?",
    answer:
      "AEO (Answer Engine Optimization) and GEO (Generative Engine Optimization) — sometimes called AI SEO — are the practice of optimizing content so AI answer engines like ChatGPT, Perplexity, Google AI Overviews, and Gemini surface and cite it. Increasingly, people learn about a person or brand from an AI-generated answer rather than a list of blue links. If those engines describe you inaccurately, that becomes many people's first impression. NoYou's AI Visibility Check shows how the major engines currently describe you and recommends content to publish so they cite the correct facts.",
  },
  {
    id: "privacy",
    question: "Is my data private? Are you GDPR and CCPA compliant?",
    answer:
      "Yes. NoYou analyzes publicly available mentions, not private accounts or messages. You can export or delete your data at any time, and we support GDPR and CCPA data-subject requests including access and erasure. For privacy-sensitive teams, NoYou's scanning engine can run fully offline using keyless sources, so no data leaves your environment. We never sell your data.",
  },
  {
    id: "sources",
    question: "What sources does NoYou scan?",
    answer:
      "Out of the box, NoYou scans DuckDuckGo (web search), Hacker News, and Reddit — all keyless, so they work immediately with no setup. You can connect Google Custom Search (CSE) for broader web coverage and large language model providers for richer AI analysis and the AI Visibility Check. Every source result passes through a relevance filter so you only see mentions that are genuinely about you.",
  },
  {
    id: "score",
    question: "How is the reputation score calculated?",
    answer:
      "The reputation score is a single 0-100 number derived from every mention NoYou finds. It weighs the volume of mentions, their sentiment (positive, neutral, negative), the assessed risk level, how recent each mention is, and the reach of the source. A higher score means a healthier reputation. Because it updates continuously, you can track the score over time and measure whether your reputation is improving or declining.",
  },
  {
    id: "remove-content",
    question: "Can NoYou remove content about me?",
    answer:
      "NoYou does not silently delete content from the internet — no tool can guarantee that. What it does is identify high-risk content, suggest the most effective cleanup actions for each case (such as removal requests, public responses, or publishing positive content to suppress negatives), and help you prioritize. For content that violates a platform's policies or the law, NoYou provides templates and guidance to request takedowns through the proper channels.",
  },
  {
    id: "pre-post-check",
    question: "What is the Pre-Post Check?",
    answer:
      "Pre-Post Check is a predictive feature that answers a simple question: will this post hurt me? Paste a draft tweet, comment, or announcement and NoYou estimates its reputational risk, highlights wording that could be misread or cause backlash, and suggests safer phrasing. It's a fast way to catch a damaging post before you publish it, rather than after it goes viral.",
  },
  {
    id: "ai-visibility-check",
    question: "What is the AI Visibility Check?",
    answer:
      "The AI Visibility Check asks the major AI answer engines — ChatGPT, Perplexity, Gemini, and Google AI Overviews — how they currently describe your brand or name. It surfaces inaccuracies, outdated facts, and missing information, then recommends content to publish so those engines cite the right facts about you. As more people rely on AI for first impressions, controlling your AI visibility is as important as ranking in search.",
  },
  {
    id: "pricing",
    question: "How much does NoYou cost?",
    answer:
      "NoYou has four plans. Free is $0 forever and includes one monitored identity, weekly keyless scans, and basic AI analysis. Pro is $29 per month for professionals and founders, with daily scans, full AI risk analysis, alerts, and unlimited Pre-Post Checks. Premium is $59 per month for executives and brands, adding hourly scans, real-time alerts, and a weekly AI Visibility Check. Enterprise is custom-priced for teams that need unlimited identities, SSO, and offline or on-prem deployment.",
  },
  {
    id: "who-is-it-for",
    question: "Who is NoYou for?",
    answer:
      "NoYou is built for founders, executives, professionals, and brands who need to control how they appear online and how AI engines describe them. If a search result, viral post, or AI answer about you could affect a deal, a hire, an investment, or your career, NoYou gives you the early warning and the playbook to respond.",
  },
];

/* ------------------------------------------------------------------ */
/* About / company                                                     */
/* ------------------------------------------------------------------ */

export const ABOUT = {
  mission:
    "Everyone deserves to control their own narrative. NoYou exists to give people and brands an honest, real-time picture of their reputation across the web and AI — and the tools to improve it.",
  story:
    "NoYou started from a simple observation: reputation now forms in places you can't see. A Reddit thread, a Hacker News comment, or an AI-generated summary can shape how thousands of people perceive you before you even know it exists. Traditional monitoring tools were expensive, noisy, and blind to AI answer engines. We built NoYou to be accurate, affordable, privacy-respecting, and ready for the AI era — with a relevance-filtered scanning engine that works on keyless public sources from day one.",
  values: [
    {
      title: "Truth over vanity",
      description:
        "We show you the real picture — good and bad — because you can't fix what you can't see.",
    },
    {
      title: "Privacy by default",
      description:
        "We work on public data, support GDPR/CCPA requests, and can run fully offline. We never sell your data.",
    },
    {
      title: "AI-era ready",
      description:
        "Search is no longer just blue links. We help you control how AI answer engines describe you, not just how you rank.",
    },
    {
      title: "Accessible to everyone",
      description:
        "A free plan that genuinely works, fair paid tiers, and no enterprise-only gatekeeping for the basics.",
    },
  ],
};
