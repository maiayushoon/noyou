# NoYou — AI-Powered Digital Identity & Reputation Management

> Your 24/7 AI-powered personal digital bodyguard. It monitors your online presence,
> analyzes risk, scores your reputation, and gives you actionable cleanup suggestions.

NoYou is the production implementation of the **Digital Identity & Reputation
Management Software** blueprint (DRSP). It scans the web and social platforms for
mentions of a person or brand, runs AI sentiment + risk analysis on every mention,
aggregates a reputation score, raises alerts on high-risk content, and recommends
(or, in future, automates) cleanup actions.

```
User → Connect accounts → Scan (web + social) → AI analysis → Reputation score
     → Dashboard + Alerts → Cleanup suggestions → Reports & Trends
```

---

## Why this design

The whole product is built around **two pluggable interfaces** so it works *today*
with zero external dependencies and scales to real integrations *tomorrow*:

| Interface | Ships with (works offline) | Drop-in later |
|-----------|----------------------------|---------------|
| `BaseConnector` (data sources) | `DemoConnector` — realistic synthetic mentions | Google CSE, X/Twitter, LinkedIn, Reddit, YouTube |
| `BaseAnalyzer` (AI) | `RuleBasedAnalyzer` — lexicon sentiment + risk | OpenAI / Anthropic / HuggingFace via `LLMAnalyzer` |

That means you can `pip install` and run the **entire end-to-end pipeline** —
scan → analyze → score → alert → dashboard — without a single API key. When you
get keys, you flip env vars and the real providers light up. Nothing else changes.

---

## Quick start

**One command** — from the repo root, the dev launcher starts the API (`:8000`) and the
dashboard (`:3002`) together, on fixed ports, freeing them first so nothing drifts:

```powershell
.\dev.ps1          # Windows (or double-click dev.bat)
./dev.sh           # macOS / Linux
```

Then open **http://localhost:3002** and sign in with the seeded demo account:

```
email:    demo@noyou.app
password: demo12345
```

- **Dashboard** (Next.js): http://localhost:3002
- **API** + Swagger docs: http://localhost:8000/docs · health: http://localhost:8000/health

**First-time setup** (the launcher auto-installs the dashboard deps; the backend venv is manual):

```bash
cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
```

**Or run the two pieces manually:**

```bash
# terminal 1 — API
cd backend && uvicorn app.main:app --reload --port 8000
# terminal 2 — dashboard
cd frontend && npm run dev            # http://localhost:3002
```

### With Docker

```bash
docker compose up --build
```

This brings up the API + a Postgres database. The app falls back to SQLite if no
`DATABASE_URL` is set, so Postgres is optional.

---

## Configuration

Copy `.env.example` to `backend/.env` and edit. Everything has a safe default — an
empty `.env` runs in full demo mode.

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENVIRONMENT` | `development` | `production` enables HSTS + refuses a default secret |
| `FRONTEND_URL` | `http://localhost:8000` | Base URL for verification/reset email links |
| `DATABASE_URL` | `sqlite:///./noyou.db` | DB connection (Postgres ready) |
| `SECRET_KEY` | dev key (auto) | JWT signing key — **set in prod** |
| `ANALYZER` | `rule_based` | `rule_based` or `llm` |
| `CONNECTORS` | `demo` | `web,hackernews,reddit_public` are keyless & real; `demo` is synthetic |
| `REQUIRE_EMAIL_VERIFICATION` | `false` | Require email confirmation before login |
| `RATE_LIMIT_PER_MINUTE` / `AUTH_RATE_LIMIT_PER_MINUTE` | `60` / `10` | Per-IP request limits |
| `SCAN_INTERVAL_MINUTES` | `360` | Background auto-scan cadence (0 = off) |
| `SEED_DEMO` | `true` | Seed the demo user + first scan on boot |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | — | For `ANALYZER=llm` |
| `GOOGLE_API_KEY` / `GOOGLE_CSE_ID` | — | For the Google connector (free 100/day) |
| `SMTP_*` | — | Email (verification, reset, alerts) |

See [`.env.example`](.env.example) for the full list, and
[`.env.production.example`](.env.production.example) for a live deployment.

---

## Repository structure

Three independently deployable apps:

| Folder | What it is | Run (dev) | Deploys to |
|--------|-----------|-----------|------------|
| **`backend/`** | FastAPI JSON **API** + data (SQLAlchemy, scanning, AI analysis) | `uvicorn app.main:app` → **:8000** | your server / Render / Fly |
| **`frontend/`** | The product **dashboard** — Next.js 14 + TypeScript + Tailwind + **lucide-react** + Recharts + Framer Motion | `npm run dev` → **:3001** | `app.noyou.app` (Vercel) |
| **`marketing/`** | Public **AI-SEO site** — Next.js (JSON-LD, `llms.txt`, sitemap) | `npm run dev` → **:3000** | `noyou.app` (Vercel) |

```
noyou/
├── backend/     FastAPI API — app/{models,schemas,api/routes,connectors,analysis,services,core,notifications}, tests/
├── frontend/    Next.js dashboard app — app/(auth) + app/(dashboard), components/, lib/  (Lucide icons, no emojis)
├── marketing/   Next.js public marketing/SEO site — app/, components/, public/{llms.txt,sitemap,privacy.html,terms.html}
├── docker-compose.yml · docker-compose.prod.yml · Caddyfile     (containerized prod stack, auto-HTTPS)
└── DEPLOYMENT.md · ARCHITECTURE.md · ROADMAP.md · SECURITY.md
```

The **backend is API-only** (no longer serves any HTML). The `frontend/` reaches it via
`NEXT_PUBLIC_API_URL` (set in `frontend/.env.local`, default `http://localhost:8000`); the backend's
`CORS_ORIGINS` allows the dashboard + marketing origins.

---

## Production features (ready for public launch)

- **Real, keyless data** — `web` (DuckDuckGo), `hackernews`, `reddit_public` connectors
  return genuine mentions with no API keys; Google CSE (free 100/day) and keyed
  providers drop in via env.
- **Predictive pre-post check** — `POST /api/v1/analyze`: paste a draft, get a
  safe / review / **do-not-post** verdict before you publish (Pro feature).
- **Public auth** — email verification + password reset (enumeration-safe), bcrypt,
  JWT, per-IP rate limiting on auth endpoints.
- **Security hardening** — CSP + security headers, request IDs, sanitized errors,
  slowapi rate limiting, and a production guard that refuses to boot on a default secret.
- **GDPR/CCPA** — one-click data export and account deletion; Privacy Policy + Terms pages.
- **Monetization** — `free / pro / premium / enterprise` plan gating with daily scan
  quotas and account limits.
- **Deploy anywhere** — gunicorn + Docker + Caddy auto-HTTPS, Postgres, with a
  step-by-step [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## The reputation score

Each mention is scored by sentiment (`positive` / `neutral` / `negative`) and a
risk level (1–5) across categories (`career`, `personal`, `privacy`, `financial`,
`legal`). The aggregate starts at 100 and is penalised by negative/risky mentions,
with recency weighting so old content matters less. See
[`scoring.py`](backend/app/services/scoring.py).

---

## Testing

```bash
cd backend
pytest -q
```

---

## Roadmap

The whole post-MVP feature list from the blueprint — predictive pre-post analysis,
automated cleanup, multi-lingual scanning, benchmarking, mobile, monetization tiers
— is mapped to concrete extension points in [`ROADMAP.md`](ROADMAP.md).

---

## Security

NoYou passed an adversarial security review (auth, SSRF/XSS, DoS, secrets, business
logic). Hardening includes a fail-closed secret-key guard, session revocation on
password reset, URL/scheme sanitization of scraped content, per-IP + per-plan rate
limiting, CSP/security headers, and GDPR data controls. The full posture — including
accepted-risk items and the pre-launch checklist — is in [`SECURITY.md`](SECURITY.md).

## License

Proprietary — © NoYou. For internal product development.
