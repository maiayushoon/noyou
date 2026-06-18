# NoYou Dashboard

Premium Next.js 14 (App Router, TypeScript strict) dashboard for **NoYou**, an
AI-powered digital reputation manager. This is the product app that sits in front
of the FastAPI backend.

## Stack

- **Next.js 14** (App Router) + **React 18** + **TypeScript** (strict)
- **Tailwind CSS** with a custom palette and the signature AI gradient
- **SWR** for data fetching, **framer-motion** for motion, **Recharts** for viz
- **lucide-react** icons (no emojis anywhere)

## Getting started

```bash
npm install
cp .env.example .env        # set NEXT_PUBLIC_API_URL if not localhost:8013
npm run dev                 # http://localhost:3001
```

The backend is expected at `NEXT_PUBLIC_API_URL` (default `http://localhost:8013`),
with all routes under `/api/v1`. Auth is JWT bearer; the token lives in
`localStorage` under `noyou_token`.

**Demo login:** `demo@noyou.app` / `demo12345`

## Scripts

| Script          | Description                       |
| --------------- | --------------------------------- |
| `npm run dev`   | Dev server on port 3001           |
| `npm run build` | Production build                  |
| `npm run start` | Serve the production build        |
| `npm run lint`  | ESLint (next/core-web-vitals)     |

## Project structure

```
app/
  (auth)/            login, register, forgot-password (public)
  (dashboard)/       protected AppShell + feature routes
    page.tsx         Overview (reference page, fully built)
  layout.tsx         root: Inter font + <Providers>
  providers.tsx      SWRConfig + AuthProvider + ToastProvider
  globals.css        Tailwind layers, tokens, AI gradient, scrollbar
components/
  ui/                Button, Card, Badge, Stat, Skeleton, EmptyState,
                     Spinner, Tooltip, SentimentBadge, RiskBadge,
                     ScoreRing, PlanGate  (barrel: components/ui)
  layout/            Sidebar, Topbar, AppShell, PageHeader, FeatureStub, nav
  motion/            FadeIn, StaggerList, FadeInItem
lib/
  api.ts             typed API client + all TS types + ApiError/PlanError
  auth.tsx           AuthProvider + useAuth()
  toast.tsx          ToastProvider + useToast()
  utils.ts           cn(), timeAgo(), band/sentiment/risk color helpers
```

## Design language

Linear × Vercel × Stripe — restrained and polished. Dark slate sidebar, light
`#f8fafc` canvas, white cards with a hairline border + soft shadow. The AI
gradient (indigo → violet → cyan) is used sparingly: the active nav indicator,
the reputation score ring, the primary CTA, and small "AI" badges. Motion is
quick (150–300ms) and honors `prefers-reduced-motion`.

## Auth & errors

- **401** anywhere → the API client clears the token and redirects to `/login`.
- **402** → surfaced as a typed `PlanError`; wrap feature content in `<PlanGate>`
  to render the upgrade upsell automatically.
