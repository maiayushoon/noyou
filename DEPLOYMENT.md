# Deploying NoYou to Production

This is a concrete, beginner-friendly guide to taking **NoYou** live for the
public. It covers what you need to obtain, three hosting options (a single VPS
with automatic HTTPS, Render.com, and Fly.io), database notes, a post-deploy
checklist, and scaling guidance.

If you just want the fastest path: **Option B (Render.com)** is the easiest.
For full control on one box, use **Option A (VPS + Docker + Caddy)**.

---

## 0. What you need to obtain first

1. **A server or hosting account** — one of:
   - A Linux VPS (e.g. DigitalOcean, Hetzner, Linode, AWS Lightsail). A small
     1–2 GB RAM instance is enough to start. *(Option A)*
   - A Render.com account (free to sign up). *(Option B)*
   - A Fly.io account + the `flyctl` CLI. *(Option C)*

2. **A domain name (optional but strongly recommended).** Buy one from any
   registrar (Namecheap, Cloudflare, Google Domains, etc.). You'll point a DNS
   record at your host. HTTPS and email both work much better with a real
   domain. You *can* run on a raw IP or a platform-provided subdomain, but
   verification/reset emails and CORS are cleaner with your own domain.

3. **An SMTP email provider** — required so NoYou can send **email
   verification** and **password-reset** messages. Any of these work:
   - **Resend** (`smtp.resend.com`, very simple, generous free tier)
   - **SendGrid** (`smtp.sendgrid.net`, user is literally `apikey`)
   - **Mailgun** (`smtp.mailgun.org`)
   - **Gmail** (`smtp.gmail.com`) — use an **App Password**, not your login
     password (requires 2FA enabled on the Google account).
   You'll need the SMTP host, port (usually `587`), username, password/API key,
   and a verified "From" address on a domain the provider lets you send from.

4. **(Optional) Google Custom Search key** — gives the app a real web-search
   source via the `google` connector. It's **free up to 100 queries/day**:
   - Create an API key in Google Cloud Console (enable "Custom Search API").
   - Create a **Programmable Search Engine** and copy its **Search engine ID**
     (the CSE id). Set "Search the entire web" on.
   - Put these in `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`.

5. **(Optional) An LLM key** — only if you set `ANALYZER=llm`. The default
   `rule_based` analyzer needs no keys. If you want LLM analysis, get an
   OpenAI or Anthropic API key and set `LLM_PROVIDER` accordingly.

---

## 1. Generate a strong SECRET_KEY

NoYou signs login tokens with `SECRET_KEY`. **Never** ship the dev default.
Generate a unique 64-hex-character key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output into `SECRET_KEY` in your `.env` (or your host's env vars).
Treat it like a password — anyone with it can forge login sessions.

---

## 2. Prepare your environment file

Copy the template and fill it in:

```bash
cp .env.production.example .env
# edit .env with your editor
```

At minimum set: `SECRET_KEY`, `DATABASE_URL` (+ `POSTGRES_PASSWORD`),
`DOMAIN`, `FRONTEND_URL`, `CORS_ORIGINS`, and the `SMTP_*` block. Every key is
documented inline in `.env.production.example`.

---

## Option A — One VPS with Docker + Caddy (automatic HTTPS)

This runs the whole stack — API (Gunicorn + Uvicorn workers), Postgres, and a
**Caddy** reverse proxy that gets and renews TLS certificates for you — with a
single command. The API is **not** exposed to the internet directly; only Caddy
listens on ports 80/443.

### A.1 Install Docker on the server
On a fresh Ubuntu box:
```bash
curl -fsSL https://get.docker.com | sh
```
This installs Docker Engine and the `docker compose` plugin.

### A.2 Point your domain at the server
In your DNS provider, create an **A record** for your domain (e.g.
`app.example.com`) pointing to the server's public IPv4 address. (Add an
**AAAA** record for IPv6 if your server has one.) Wait for DNS to propagate —
you can check with `ping app.example.com`.

> Caddy needs the domain to already resolve to this server before it can obtain
> a certificate, because Let's Encrypt validates by reaching your server over
> HTTP/HTTPS.

### A.3 Get the code and configure
```bash
git clone <your-repo-url> noyou && cd noyou
cp .env.production.example .env
# edit .env: set DOMAIN=app.example.com, FRONTEND_URL=https://app.example.com,
# CORS_ORIGINS=https://app.example.com, SECRET_KEY, POSTGRES_PASSWORD, SMTP_*
```

### A.4 Launch
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

That's it. **How the automatic TLS works:** Caddy reads `DOMAIN` from your
`.env`, requests a certificate from Let's Encrypt (validated because your DNS
already points here), serves `https://app.example.com`, redirects HTTP→HTTPS,
and **auto-renews** the cert before it expires. Certs are stored in the
`caddy_data` volume so restarts don't re-request them.

### A.5 Verify
```bash
docker compose -f docker-compose.prod.yml ps          # all services "Up"/healthy
curl -fsS https://app.example.com/health               # {"status":"ok",...}
docker compose -f docker-compose.prod.yml logs -f caddy # watch cert issuance
```
Open `https://app.example.com` in a browser — you should see the dashboard with
a valid padlock.

### A.6 Common operations
```bash
# View API logs
docker compose -f docker-compose.prod.yml logs -f api
# Update to new code
git pull && docker compose -f docker-compose.prod.yml up -d --build
# Stop everything
docker compose -f docker-compose.prod.yml down
```

---

## Option B — Render.com (managed, easiest)

Render builds your Docker image, runs it, gives you HTTPS automatically, and
manages Postgres for you. No server administration.

### B.1 Create the Postgres database
1. In the Render dashboard: **New → PostgreSQL**.
2. Pick a name/region/plan and create it.
3. Copy the **Internal Database URL**. It looks like
   `postgres://user:pass@host/dbname`. NoYou needs the SQLAlchemy form:
   change the scheme to `postgresql+psycopg2://...` (keep the rest identical).

### B.2 Create the Web Service
1. **New → Web Service**, connect your Git repo.
2. **Runtime: Docker.** Set **Dockerfile Path** to `backend/Dockerfile.prod`
   and **Docker Build Context Directory** to `backend`.
3. Render auto-detects the exposed port `8000` and the `CMD` (Gunicorn). No
   start command needed.

### B.3 Set environment variables
In the service's **Environment** tab, add (from your `.env` values):
`ENVIRONMENT=production`, `DATABASE_URL` (the `postgresql+psycopg2://…` form
from B.1), `SECRET_KEY`, `FRONTEND_URL` (your Render URL or custom domain,
`https://…`), `CORS_ORIGINS` (same), `SEED_DEMO=false`, `CONNECTORS=web,hackernews,reddit_public`,
the `SMTP_*` block, and `NOTIFY_CHANNEL=email`. Set
`REQUIRE_EMAIL_VERIFICATION=false` for the first deploy.

> Note: Render runs the container without your repo's `frontend/` volume mount,
> so `/` returns the JSON API message rather than the bundled dashboard. The
> full JSON API and `/docs` work normally. If you want the dashboard served too,
> host the `frontend/` directory as a Render **Static Site** pointing at your
> API, or switch to Option A.

### B.4 Deploy & HTTPS
Click **Create Web Service**. Render builds and deploys, and gives you a
`https://<name>.onrender.com` URL with **HTTPS already on**. To use your own
domain: **Settings → Custom Domains → Add**, then create the CNAME record Render
shows you. Render provisions the TLS cert automatically. After adding a custom
domain, update `FRONTEND_URL` and `CORS_ORIGINS` to it and redeploy.

---

## Option C — Fly.io

Fly runs your container close to users with built-in HTTPS.

```bash
# 1) Install flyctl and sign in
#    (see https://fly.io/docs/flyctl/install/)
fly auth login

# 2) From the repo root, create the app. When asked, point it at the prod
#    Dockerfile and DON'T deploy yet.
fly launch --no-deploy --dockerfile backend/Dockerfile.prod

# 3) Create a managed Postgres and attach it (sets DATABASE_URL for you).
fly postgres create
fly postgres attach <your-postgres-app-name>
#    Fly sets DATABASE_URL as postgres://...  — NoYou needs the +psycopg2 form.
#    Override it explicitly:
fly secrets set DATABASE_URL='postgresql+psycopg2://<user>:<pass>@<host>:5432/<db>'

# 4) Set the rest of your secrets (never commit these).
fly secrets set SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") \
  ENVIRONMENT=production SEED_DEMO=false \
  CONNECTORS=web,hackernews,reddit_public \
  NOTIFY_CHANNEL=email SMTP_HOST=... SMTP_PORT=587 SMTP_USER=... \
  SMTP_PASSWORD=... SMTP_FROM=alerts@example.com \
  FRONTEND_URL=https://<app>.fly.dev CORS_ORIGINS=https://<app>.fly.dev

# 5) Make sure the service listens on the internal port 8000 (in fly.toml,
#    [http_service] internal_port = 8000). Fly terminates TLS for you.
fly deploy
```

Add a custom domain with `fly certs add app.example.com` and the DNS records
Fly prints. Like Render, Fly runs without the `frontend/` mount, so `/` serves
the JSON message and the API/`/docs` work normally.

---

## 2.5 Database migrations

On boot the app calls `Base.metadata.create_all(...)`, which **auto-creates any
missing tables**. For a brand-new database this is all you need — just start the
app and the schema appears.

**Important:** `create_all` does **not** alter existing tables. If you later
change a model (add/rename a column, change a type), `create_all` won't apply
it. NoYou now ships with **Alembic** wired up for exactly this case — see the
**[Database migrations (Alembic)](#database-migrations-alembic)** section below
for the full workflow.

---

## 3. Post-deploy checklist

Work through these once the app is reachable:

- [ ] **`/health` returns OK** — `curl https://<your-domain>/health` →
      `{"status":"ok",...}`.
- [ ] **HTTPS works** — the browser shows a valid padlock; `http://` redirects
      to `https://`.
- [ ] **`SECRET_KEY` is the generated value**, not the dev default.
- [ ] **`SEED_DEMO=false`** so no demo account/data exists in production.
- [ ] **`CONNECTORS` is set to real sources** (e.g.
      `web,hackernews,reddit_public`), not `demo`.
- [ ] **`CORS_ORIGINS` is your real domain only** (not `*`).
- [ ] **`FRONTEND_URL` is your public HTTPS URL** (used in email links).
- [ ] **SMTP works** — register a test account and confirm the verification and
      password-reset emails arrive (check spam). Watch the API logs if not.
- [ ] **Flip `REQUIRE_EMAIL_VERIFICATION=true`** *after* SMTP is confirmed, then
      redeploy/restart. (Do this last — enabling it before email works locks new
      users out.)
- [ ] **Register a real account** end-to-end: sign up → verify → log in → run a
      scan → see results.
- [ ] **Back up the database** — schedule regular Postgres backups (managed
      providers do this; on a VPS, snapshot the `pgdata` volume or run
      `pg_dump` on a cron).

---

## 4. Scaling notes

NoYou is a standard Gunicorn + Uvicorn ASGI app, so the usual levers apply:

- **Gunicorn workers.** More workers = more concurrent requests. The default is
  `(2 × CPU) + 1`. On small/shared hosts, pin it explicitly with the
  `WEB_CONCURRENCY` env var (e.g. `WEB_CONCURRENCY=3`). Each worker is a full
  Python process, so size it against available RAM. See `backend/gunicorn_conf.py`
  for all tunables (`GUNICORN_TIMEOUT`, `GUNICORN_MAX_REQUESTS`, etc.).

- **⚠️ The background scheduler and multiple instances.** NoYou runs scans on an
  **in-process APScheduler** that starts inside the app on boot. With a single
  instance this is fine. But if you run **multiple workers/instances** (more
  Gunicorn workers, or several Render/Fly machines), each process starts its own
  scheduler and **scans will run multiple times** — wasting API quota and
  duplicating work. Before scaling horizontally, move scanning **out of the web
  process**:
    - Run a **single dedicated worker** container/process that owns the
      scheduler, and disable the in-process scheduler in the web instances; **or**
    - Replace APScheduler with an external scheduler (system cron / a platform
      cron job / Celery beat) that triggers a scan command on a schedule.
  The goal: exactly one thing runs scans, no matter how many web replicas exist.

- **Postgres connection pooling.** Each Gunicorn worker keeps its own SQLAlchemy
  connection pool, so total DB connections ≈ workers × pool size. As you add
  workers/instances you can exhaust Postgres' `max_connections`. Put a pooler
  like **PgBouncer** (transaction pooling) in front of Postgres, and/or cap the
  SQLAlchemy pool size. Managed Postgres (Render/Fly/RDS) often offers a pooled
  connection string — prefer it when running many workers.

- **Right-size before scaling out.** Vertical first (a bigger box, a few more
  workers) is simpler than horizontal. Only add instances once you've split the
  scheduler out as described above.

---

## Database migrations (Alembic)

NoYou ships with **Alembic** configured in `backend/` for versioned schema
changes. It is the recommended way to evolve the schema on a database that
already holds real data (Postgres in production), since `create_all` only
creates missing tables and never alters existing ones.

### Zero-config dev still works
For local development you don't have to touch Alembic at all: on boot the app
still runs `Base.metadata.create_all(...)`, so a fresh SQLite database gets its
tables automatically. Alembic is there when you need controlled, reversible
schema changes — especially against a production Postgres with live data.

### How it's wired
- `backend/alembic.ini` — Alembic config. `sqlalchemy.url` is intentionally
  **left blank**.
- `backend/alembic/env.py` — reads the database URL from the app
  (`app.core.config.settings.database_url`) and the schema from
  `Base.metadata` (importing `app.models` so every table is registered). It sets
  `render_as_batch=True` (so column ALTERs also work on SQLite) and renders the
  custom `GUID` type portably (native `UUID` on Postgres, `String(36)`
  elsewhere). There is no DB URL hard-coded anywhere — it always follows
  `DATABASE_URL`.
- `backend/alembic/versions/` — the migration scripts. The initial migration
  (`*_initial_schema.py`) creates all current tables: `users`, `accounts`,
  `mentions`, `analyses`, `alerts`, `scans`, `cleanup_actions`,
  `verification_tokens`.

### Running migrations on deploy
Run this from `backend/` (with the app's virtualenv active and `DATABASE_URL`
set to the target database) **before** starting/restarting the app:

```bash
cd backend
alembic upgrade head
```

This applies any pending migrations and is a no-op once the database is current,
so it is safe to run on every deploy. Typical placement:
- **Option A (VPS + Docker):** run it as a one-off before bringing the API up,
  e.g. `docker compose -f docker-compose.prod.yml run --rm api alembic upgrade head`,
  then `... up -d`.
- **Render / Fly:** add `alembic upgrade head` as a pre-deploy / release command
  (Render "Pre-Deploy Command", Fly `[deploy] release_command`), or run it once
  via a shell into the instance.

### Recommended Postgres flow
1. Point `DATABASE_URL` at your Postgres instance, in the SQLAlchemy form
   `postgresql+psycopg2://user:pass@host:5432/dbname` (the `psycopg2-binary`
   driver is already in `requirements.txt`).
2. On a brand-new Postgres database, bring the schema up with:
   ```bash
   cd backend
   alembic upgrade head
   ```
   (If the database already has the tables from a prior `create_all` run, stamp
   it as current instead of re-creating: `alembic stamp head`.)
3. When you change a model later, autogenerate and review a new migration, then
   apply it:
   ```bash
   alembic revision --autogenerate -m "describe change"
   # review the generated file in alembic/versions/, then:
   alembic upgrade head
   ```
   Always **read the autogenerated script** before applying — Alembic can't infer
   intent for renames or data backfills, and those need hand-editing.

Other handy commands: `alembic current` (show the applied revision),
`alembic history` (list migrations), `alembic downgrade -1` (roll back one).
