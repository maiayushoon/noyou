# Security

NoYou underwent an adversarial security review (5 dimensions: authN/authZ,
SSRF/injection/XSS, rate-limit/DoS, secrets/config/headers, business logic). Each
finding was independently verified. This document records what was fixed and the
remaining accepted-risk items, so the posture is transparent rather than implied.

## Reporting a vulnerability

Email **security@noyou.app** with details and reproduction steps. Please do not open
public issues for security reports.

## Hardened in the production pass

| Area | Control |
|------|---------|
| **Secret key** | `get_settings()` refuses to boot in any non-`development` environment with a placeholder/weak (`< 32` char) `SECRET_KEY`, and auto-generates a strong ephemeral key in development. No shared/default key ever signs real tokens. |
| **Session revocation** | Access tokens carry `iat`; a password reset bumps `User.password_changed_at`, and `get_current_user` rejects tokens issued before it — so resetting a password kills stolen sessions. |
| **Stored XSS** | External/scraped URLs are scheme-sanitized to `http(s)` on ingest (`scanning._safe_url`) and again in the UI (`safeUrl`); all dynamic content renders via Alpine `x-text` (escaped), never `x-html`. Outbound links use `rel="noopener noreferrer nofollow"`. |
| **DoS / worker exhaustion** | Scans run asynchronously (202 + poll) off the request worker; queries per scan are capped (`MAX_QUERIES_PER_SCAN`); all connector HTTP calls have timeouts and never raise. |
| **Rate limiting** | Global per-IP limit on every route + tighter limit on auth/password endpoints (slowapi). Real client IP honored behind the proxy (`forwarded_allow_ips`). |
| **Plan integrity** | Connectors are filtered to the user's plan at scan time (`plan_allows_connector`); free users get keyless real sources, keyed providers are paid. Daily scan quota + account limits enforced. |
| **Transport / headers** | CSP, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, HSTS in production (app + Caddy), request IDs, sanitized 500s (no stack traces in prod). |
| **Docs surface** | `/docs`, `/redoc`, `/openapi.json` are disabled when `ENVIRONMENT=production`. |
| **Authorization** | Every route filters by `current_user.id`; every mutation verifies row ownership (no IDOR). UUID ids. |
| **Data protection** | GDPR export excludes `password_hash` and OAuth tokens; account deletion cascades to all related rows. Enumeration-safe password reset / resend. |
| **Input bounds** | List endpoints cap `limit` (`le=200`); draft analysis caps text length. |
| **Container** | Production image runs as a non-root user; multi-stage build with no compiler in the runtime layer. |

## Accepted risk / hardening backlog

These are known and intentionally deferred for v1. They are low-impact for an early
public launch; the rationale and fix are recorded here.

1. **Quota / account-limit race (TOCTOU)** — concurrent requests can momentarily
   exceed the daily scan or account cap by a small margin (count-then-insert is not
   atomic). Impact: a user gets one or two extra scans/accounts, not a breach.
   *Fix when needed:* a per-user row lock (`SELECT … FOR UPDATE`) or a DB constraint.
   (No effect on SQLite single-writer; relevant only at Postgres + multi-worker scale.)

2. **Access-token lifetime (24h)** — tokens are valid for `ACCESS_TOKEN_EXPIRE_MINUTES`
   (default 1440). Password reset revokes them (above), but there is no general logout
   denylist. *Fix when needed:* refresh-token rotation + a short access lifetime, or a
   per-user token-version claim. Lower the env var to shorten the window now.

3. **CSP allows `unsafe-inline`/`unsafe-eval`** — required by the zero-build frontend
   (Tailwind CDN + Alpine). Scoped to known CDN origins. *Fix when needed:* self-host
   built, hashed assets and switch to a nonce-based CSP.

4. **Data export builds the full response in memory** — fine for typical per-user data
   sizes. *Fix when needed:* stream the JSON or generate it as a background job with a
   download link; rate-limit the endpoint tighter than the global default.

5. **Registration reveals whether an email exists** — a deliberate UX trade-off (users
   need to know an address is taken). *Fix when needed:* return a generic "check your
   inbox" response and email the existing user instead.

6. **In-process scheduler** — the APScheduler scan loop runs in the app process; with
   more than one instance it would double-run. *Fix at scale:* move scans to an external
   worker/queue (Celery/RQ/Cloud Tasks). See `DEPLOYMENT.md` scaling notes.

## Pre-launch checklist

- [ ] Set a strong unique `SECRET_KEY` and `ENVIRONMENT=production`.
- [ ] Set `CONNECTORS=web,hackernews,reddit_public` (+ keyed ones if you have keys).
- [ ] Configure SMTP, then set `REQUIRE_EMAIL_VERIFICATION=true`.
- [ ] Set `CORS_ORIGINS` and `FRONTEND_URL` to your real domain; `SEED_DEMO=false`.
- [ ] Serve only over HTTPS (Caddy does this automatically).
