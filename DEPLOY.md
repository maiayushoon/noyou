# Deploying NoYou

A concise, one-path production guide. It brings up the API (FastAPI + gunicorn/
uvicorn) and the Next.js dashboard with Docker Compose. SQLite works out of the
box; Postgres is one flag away.

> Already have the stack and just want it running? Jump to
> [4. Bring it up](#4-bring-it-up).

---

## 1. Prerequisites

- Docker Engine 24+ and the Docker Compose plugin (`docker compose version`).
- A domain + TLS terminator (a reverse proxy such as Caddy, nginx, or your cloud
  load balancer) in front of the two containers. The API enables HSTS and only
  serves OAuth callbacks correctly when reached over **HTTPS** in production.

---

## 2. Configure environment

All configuration is read from a single `.env` file in the repo root. Start from
the template — every key is documented there:

```bash
cp .env.example .env
```

Then set the production-critical values. The minimum you must change:

| Variable | Why it matters |
| --- | --- |
| `ENVIRONMENT=production` | Enables HSTS, hides `/docs`, and makes the app **refuse to boot** with a weak `SECRET_KEY` (fail-closed). |
| `SECRET_KEY` | Signs JWTs and (by default) derives the token-encryption key. Must be strong and unique — generate with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `DATABASE_URL` | `sqlite:////data/noyou.db` (default, persisted on a volume) **or** a Postgres URL, e.g. `postgresql+psycopg2://noyou:STRONGPASS@db:5432/noyou`. |
| `FRONTEND_URL` | Public HTTPS URL of the dashboard (e.g. `https://app.example.com`). Used to build email links and the OAuth return redirect. |
| `CORS_ORIGINS` | Comma-separated list of allowed browser origins — include `FRONTEND_URL`. |
| `OAUTH_CALLBACK_BASE_URL` | Public HTTPS URL of **this API** (e.g. `https://api.example.com`). The provider `redirect_uri` is built from this, so it must match what's registered in each OAuth app's console. |
| `NEXT_PUBLIC_API_URL` | Public URL of the API as reached from the **browser** (e.g. `https://api.example.com`). Baked into the dashboard at build time. |

Optional, set as needed (all documented in `.env.example`):

- **Email** (`NOTIFY_CHANNEL`, `RESEND_API_KEY` or `SMTP_*`) — required if you set
  `REQUIRE_EMAIL_VERIFICATION=true`.
- **Connectors** — for a live launch: `CONNECTORS=web,hackernews,reddit_public,googlenews,bing`.
- **OAuth account-linking (Connections)** — `GOOGLE_OAUTH_*`, `REDDIT_OAUTH_*`,
  `THREADS_*`, `INSTAGRAM_*`, `TOKEN_ENCRYPTION_KEY`.
- **Stripe billing** — `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, price IDs.

> Tip: pin `TOKEN_ENCRYPTION_KEY` (a urlsafe-base64 32-byte Fernet key) so rotating
> `SECRET_KEY` doesn't invalidate already-linked OAuth tokens.

---

## 3. Database & migrations

NoYou ships Alembic migrations (`backend/alembic`). `alembic upgrade head` is the
source of truth for the schema in production.

**Using Postgres** (recommended for multi-worker / multi-instance deployments),
add these to `.env`:

```dotenv
DATABASE_URL=postgresql+psycopg2://noyou:STRONGPASS@db:5432/noyou
POSTGRES_USER=noyou
POSTGRES_PASSWORD=STRONGPASS
POSTGRES_DB=noyou
```

Start the database and run migrations before serving traffic:

```bash
# Start Postgres (the `postgres` compose profile).
docker compose --profile postgres up -d db

# Apply migrations inside the API image (alembic reads DATABASE_URL from settings).
docker compose --profile postgres run --rm api alembic upgrade head
```

**Using SQLite** (default): the file lives on the `apidata` volume at
`/data/noyou.db` and the app creates the tables on first boot. You can still apply
migrations explicitly:

```bash
docker compose run --rm api alembic upgrade head
```

---

## 4. Bring it up

**SQLite (default):**

```bash
docker compose up -d --build
```

**Postgres:**

```bash
docker compose --profile postgres up -d --build
```

This builds and starts:

- **api** on `:8000` — gunicorn managing `WEB_CONCURRENCY` uvicorn workers.
- **web** on `:3001` — the Next.js dashboard via `next start`.
- **db** on `:5432` — only under the `postgres` profile.

Point your reverse proxy at `:8000` (API) and `:3001` (dashboard), terminating TLS.

---

## 5. Verify

```bash
# API liveness (also wired as the container HEALTHCHECK).
curl -fsS http://localhost:8000/health
# → {"status":"ok","service":"NoYou","version":"..."}

docker compose ps          # both services Up/healthy
docker compose logs -f api # watch startup ("NoYou v… ready (env=production)")
```

Open the dashboard at `FRONTEND_URL` and sign in (the demo account is
`DEMO_EMAIL` / `DEMO_PASSWORD` when `SEED_DEMO=true`).

---

## 6. Operating notes

- **Scaling:** tune `WEB_CONCURRENCY` (≈ `2 × vCPU + 1`). With more than one worker
  or instance, use **Postgres**, not SQLite. After scaling out, prefer running the
  scheduler in a single instance to avoid duplicate background scans.
- **Upgrades:** `git pull && docker compose --profile postgres run --rm api alembic upgrade head`
  then `docker compose up -d --build`.
- **Backups:** back up the Postgres volume (`pgdata`) or the SQLite volume
  (`apidata`) regularly.
- **Secrets:** never commit `.env`. The API fails closed in production if
  `SECRET_KEY` is weak or missing — that's by design.

## Security hardening (production)

- **Egress controls (SSRF):** the Mastodon connector lets users supply their own
  instance URL. We validate the resolved host and reject private/loopback/link-local
  IPs, but a DNS-rebinding attacker could still target internal hosts. Deny the
  backend's outbound access to RFC-1918 / link-local ranges via a firewall or egress
  proxy so internal services are unreachable regardless.
- **Secrets:** set a strong unique `SECRET_KEY` (the app refuses to boot in
  production with a weak one). It also derives the token-encryption key — rotating it
  invalidates stored OAuth tokens (users re-link). Use `TOKEN_ENCRYPTION_KEY` to
  decouple them if you rotate `SECRET_KEY` independently.
- **HTTPS only:** set `FRONTEND_URL`/`OAUTH_CALLBACK_BASE_URL` to https origins; OAuth
  redirect URIs must match exactly. HSTS is enabled automatically in production.
