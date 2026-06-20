# NoYou — Getting Every API Key (from scratch)

This is the complete, step‑by‑step guide to obtaining every credential NoYou can
use, and exactly which line in `backend/.env` to paste it into.

**You do not need all of these.** NoYou runs end‑to‑end with **zero keys** (real
data via keyless sources + the offline trained model). Add keys to unlock more.

> **Where keys go:** all of these live in **`backend/.env`** (copy `.env.example`
> to `backend/.env` first). That file is gitignored — never commit it.
>
> **`{BACKEND_URL}`** below = your backend's public address. Locally that's
> `http://localhost:8000`; in production it's e.g. `https://api.yourdomain.com`.
> Set it in `OAUTH_CALLBACK_BASE_URL` so OAuth redirect URIs match exactly.

---

## Priority order (do these in order)

| Tier | What | Cost | Needed for |
|------|------|------|-----------|
| 0 | `SECRET_KEY` (+ optional `TOKEN_ENCRYPTION_KEY`) | free, self‑generated | **required to run** |
| 1 | Keyless sources (already on) | free, nothing to do | real data out of the box |
| 2 | Hugging Face / Google CSE / YouTube / Reddit search | free | smarter AI + more sources |
| 3 | OAuth: Google, Reddit, Threads, Instagram | free* | "Connect your accounts" |
| 4 | Resend (email) + Stripe (billing) | free tiers | alerts + charging money |
| 5 | X/Twitter, OpenAI/Anthropic | paid | optional upgrades |

\* free to set up; some need app review (noted below).

---

## TIER 0 — Required (generate yourself, 30 seconds)

### `SECRET_KEY` (mandatory in production)
Signs login tokens and derives the OAuth‑token encryption key. Run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output:
```
SECRET_KEY=<paste here>
```
> The app **refuses to boot** in production with a weak/default key.

### `TOKEN_ENCRYPTION_KEY` (optional)
By default the token‑encryption key is derived from `SECRET_KEY`. Only set this if
you want to rotate `SECRET_KEY` without invalidating stored OAuth tokens:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
```
TOKEN_ENCRYPTION_KEY=<paste here>
```

---

## TIER 1 — Keyless real data (nothing to do ✅)

These need **no keys** and are already enabled:
```
CONNECTORS=web,hackernews,reddit_public,googlenews,bing
```
- `web` — DuckDuckGo · `hackernews` — Hacker News · `reddit_public` — Reddit search
- `googlenews` — Google News RSS · `bing` — Bing News RSS

The offline AI also needs no keys:
```
ANALYZER=trained        # our own trained model (free, offline). Or: rule_based
```

---

## TIER 2 — Free upgrades

### Hugging Face — free LLM analysis · `HUGGINGFACE_API_KEY`
1. Sign up at **https://huggingface.co/join**
2. Click your avatar → **Settings** → **Access Tokens** (https://huggingface.co/settings/tokens)
3. **+ Create new token** → type **Read** → name it → **Create token**
4. Copy the `hf_...` value.
```
ANALYZER=llm
LLM_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_xxxxxxxx
```
> Free tier is rate‑limited. If unsure, keep `ANALYZER=trained` (our offline model).

### Google Programmable Search — `GOOGLE_API_KEY` + `GOOGLE_CSE_ID`
Free 100 searches/day. (This is the **search connector** — different from the
Google **OAuth** in Tier 3.)
1. Go to **https://console.cloud.google.com** → top bar → **Select a project** →
   **New Project** → name it (e.g. `noyou`) → **Create**.
2. **APIs & Services** → **Library** → search **"Custom Search API"** → **Enable**.
3. **APIs & Services** → **Credentials** → **+ Create credentials** → **API key** →
   copy it → that's `GOOGLE_API_KEY`.
4. Go to **https://programmablesearchengine.google.com/controlpanel/create** →
   name it, choose **"Search the entire web"** → **Create**.
5. Open the engine → **Overview** → copy the **Search engine ID** → that's `GOOGLE_CSE_ID`.
```
GOOGLE_API_KEY=AIza...
GOOGLE_CSE_ID=xxxxxxxxxxxx
CONNECTORS=web,hackernews,reddit_public,googlenews,bing,google
```

### YouTube Data API — `YOUTUBE_API_KEY` (optional search source)
1. Same Google Cloud project → **Library** → **"YouTube Data API v3"** → **Enable**.
2. **Credentials** → **+ Create credentials** → **API key** → copy.
```
YOUTUBE_API_KEY=AIza...
```

### Reddit search app — `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET`
(This is the **search connector** — different from the Reddit **OAuth** in Tier 3.)
1. Go to **https://www.reddit.com/prefs/apps** → **create another app…**
2. Type: **script**. Name: `noyou`. redirect uri: `http://localhost:8000` (unused here).
3. **create app**. The string under the app name = `REDDIT_CLIENT_ID`; **secret** = `REDDIT_CLIENT_SECRET`.
```
REDDIT_CLIENT_ID=xxxxxxxx
REDDIT_CLIENT_SECRET=xxxxxxxx
REDDIT_USER_AGENT=noyou/1.0 by u/yourusername
```

---

## TIER 3 — OAuth account linking ("Connections")

These let users **connect their own accounts**. Each redirect URI must be
**exactly** `{BACKEND_URL}/api/v1/connections/<provider>/callback`.

### Mastodon — **no keys needed** ✅
Self‑registers per instance. Users just type their instance URL (e.g. `mastodon.social`).

### Google / YouTube OAuth — `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET`
1. **https://console.cloud.google.com** (same project) → **Library** → enable
   **"YouTube Data API v3"** (if not already).
2. **APIs & Services** → **OAuth consent screen** → **External** → fill app name,
   support email → add scope `…/auth/youtube.readonly` → save. (Submit for Google's
   free verification before going past 100 test users.)
3. **Credentials** → **+ Create credentials** → **OAuth client ID** → type **Web
   application**.
4. **Authorized redirect URIs** → **Add URI**:
   `{BACKEND_URL}/api/v1/connections/youtube/callback`
5. **Create** → copy **Client ID** + **Client secret**.
```
GOOGLE_OAUTH_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxx
```

### Reddit OAuth — `REDDIT_OAUTH_CLIENT_ID` + `REDDIT_OAUTH_CLIENT_SECRET`
1. **https://www.reddit.com/prefs/apps** → **create another app…**
2. Type: **web app**. redirect uri:
   `{BACKEND_URL}/api/v1/connections/reddit/callback`
3. **create app** → id (under the name) + **secret**.
4. ⚠️ As of Nov 2025 Reddit **pre‑approves all apps** — expect a 2–4 week wait
   before the keys work in production.
```
REDDIT_OAUTH_CLIENT_ID=xxxxxxxx
REDDIT_OAUTH_CLIENT_SECRET=xxxxxxxx
```

### Threads — `THREADS_APP_ID` + `THREADS_APP_SECRET`
1. **https://developers.facebook.com** → log in → **My Apps** → **Create App**.
2. Choose use case **"Access the Threads API"** (Business app). Create it.
3. Add the **Threads** product → **Settings** → set the redirect/callback:
   `{BACKEND_URL}/api/v1/connections/threads/callback`
4. **App settings** → **Basic** → copy **App ID** + **App Secret**.
```
THREADS_APP_ID=xxxxxxxx
THREADS_APP_SECRET=xxxxxxxx
```

### Instagram — `INSTAGRAM_APP_ID` + `INSTAGRAM_APP_SECRET`
1. **https://developers.facebook.com** → **Create App** (Business).
2. Add product **"Instagram"** → **"Instagram API with Instagram Login"**.
3. Set the OAuth redirect URI:
   `{BACKEND_URL}/api/v1/connections/instagram/callback`
4. **App settings** → **Basic** → copy **App ID** + **App Secret**.
5. ℹ️ Users must have a **Professional** (Business/Creator) Instagram account.
```
INSTAGRAM_APP_ID=xxxxxxxx
INSTAGRAM_APP_SECRET=xxxxxxxx
```

> X/Twitter and TikTok OAuth are also supported in code but need paid access (X) or
> app review (TikTok). Add `X_OAUTH_*` / `TIKTOK_*` later if you want them.

---

## TIER 4 — Email + Billing

### Email: Resend (recommended) — `RESEND_API_KEY`
Powers verification emails, alerts, and the weekly digest.
1. Sign up at **https://resend.com**.
2. **API Keys** → **Create API Key** → copy the `re_...` value.
3. **Domains** → **Add Domain** → add the DNS records it shows (at your domain
   registrar) → wait for **Verified**.
```
NOTIFY_CHANNEL=resend
RESEND_API_KEY=re_xxxxxxxx
SMTP_FROM=alerts@yourdomain.com
```
**Or plain SMTP (e.g. Gmail app password):**
```
NOTIFY_CHANNEL=email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM=you@gmail.com
```

### Billing: Stripe — `STRIPE_*`
1. Sign up at **https://dashboard.stripe.com**.
2. **Developers** → **API keys** → copy **Secret key** (`sk_...`) and
   **Publishable key** (`pk_...`).
3. **Product catalog** → **+ Add product** → create three products (**Pro**,
   **Premium**, **Enterprise**), each with a recurring price. Open each price and
   copy its **Price ID** (`price_...`).
4. **Developers** → **Webhooks** → **Add endpoint**:
   - URL: `{BACKEND_URL}/api/v1/billing/webhook`
   - Events: `checkout.session.completed`, `customer.subscription.created`,
     `customer.subscription.updated`, `customer.subscription.deleted`
   - **Add endpoint** → click it → **Reveal** the **Signing secret** (`whsec_...`).
```
STRIPE_SECRET_KEY=sk_live_xxxx        # use sk_test_ while testing
STRIPE_PUBLISHABLE_KEY=pk_live_xxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxx
STRIPE_PRICE_PRO=price_xxxx
STRIPE_PRICE_PREMIUM=price_xxxx
STRIPE_PRICE_ENTERPRISE=price_xxxx
```

---

## TIER 5 — Optional paid upgrades

### X / Twitter (search) — `TWITTER_BEARER_TOKEN`
1. **https://developer.x.com** → sign up (now a **paid** plan).
2. Create a Project + App → **Keys and tokens** → copy the **Bearer Token**.
```
TWITTER_BEARER_TOKEN=xxxx
CONNECTORS=...,twitter
```

### OpenAI — `OPENAI_API_KEY` (paid LLM)
1. **https://platform.openai.com** → **API keys** → **Create new secret key** (`sk-...`).
2. Add a payment method under **Billing**.
```
ANALYZER=llm
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxx
```

### Anthropic — `ANTHROPIC_API_KEY` (paid LLM)
1. **https://console.anthropic.com** → **API Keys** → **Create Key** (`sk-ant-...`).
```
ANALYZER=llm
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxx
```

---

## After editing `.env`
```bash
# from the backend/ folder, with the venv active:
alembic upgrade head        # if using Postgres in production
python -m uvicorn app.main:app --reload   # restart to load new keys
```

## Quick "minimum viable launch" set
For a real public launch you really only need:
- **`SECRET_KEY`** (Tier 0) — required
- **Resend** (Tier 4) — so verification/alert emails send
- **Stripe** (Tier 4) — only if you charge money
- Everything else is optional and the product still works without it.
