# NoYou — Roadmap (MVP → future use cases)

Every post-MVP item from the DRSP blueprint, mapped to the **exact extension point**
in this codebase. The architecture was built so each is an additive change, not a
rewrite.

## ✅ Shipped in this MVP

- User registration & account linking (`api/routes/auth.py`, `accounts.py`)
- Web & social scanning via pluggable connectors (`connectors/`)
- AI risk analysis: sentiment + risk category + context (`analysis/`)
- Reputation score + dashboard (`services/scoring.py`, `api/routes/dashboard.py`)
- Alerts & notifications (`services/alerts.py`, `notifications/`)
- Cleanup suggestions (`services/cleanup.py`)
- Reports & trends (`services/reports.py`)
- 24/7 automated scanning (`core/scheduler.py`)
- Zero-build dashboard UI (`frontend/`)

## 🔜 Near term

| Feature | Where it plugs in | Notes |
|---------|-------------------|-------|
| Real Google/X/Reddit/YouTube data | `connectors/providers.py` | Skeletons exist; add API keys to `.env`, set `CONNECTORS=` |
| LLM-grade analysis | `analysis/llm.py` | Set `ANALYZER=llm` + provider key |
| Async / queued scans | `services/scanning.py:run_scan` | Wrap as a Celery/RQ task; API already calls one function |
| Email + push delivery | `notifications/dispatcher.py` | Add a `PushChannel` (Firebase/OneSignal) alongside email |
| Password reset / email verify | `api/routes/auth.py` | Add token table + SMTP flow |
| Rate limiting & API keys | new `core/ratelimit.py` middleware | For the Enterprise "API access" tier |

## 🚀 Post-MVP (blueprint Step 9–11)

| Future use case | Design seam |
|-----------------|-------------|
| **Predictive pre-post analysis** ("will this post hurt me?") | Reuse `BaseAnalyzer` on user-drafted text via a new `POST /analyze` endpoint — no model change needed |
| **Automated cleanup** (auto-delete / takedown) | `CleanupAction.automated=True`; add an executor that calls the source connector's (future) `remove()` method |
| **Multi-account / brand monitoring** | Already modeled: `User 1─* Account`; add an `Organization` parent for teams |
| **Historical trends & competitor benchmarking** | `services/reports.py` + store competitor subjects as Accounts; compare score series |
| **Multi-lingual scanning** | Swap lexicon for language-aware models in `analysis/`; `lexicon.py` is data-only by design |
| **Mobile app** | The JSON API (`/api/v1`) is the contract; build native clients against it |
| **Gamified reputation tracking** | Derive streaks/badges from `Scan.score_after` history already persisted |

## 💰 Monetization tiers (blueprint Step 10)

`User.plan` already exists (`free | pro | premium | enterprise`). Gate features with a
dependency:

```python
def require_plan(*allowed):
    def dep(user: User = Depends(get_current_user)):
        if user.plan not in allowed:
            raise HTTPException(402, "Upgrade required")
        return user
    return dep
```

| Tier | Gated capability |
|------|------------------|
| Free | basic scanning + alerts (current default) |
| Pro ($29/mo) | real-time monitoring, multi-account, cleanup suggestions |
| Premium ($59/mo) | predictive AI, historical analytics, benchmarking |
| Enterprise | brand monitoring, multi-user, API access, custom reports |

## 🛡️ Compliance & scale (blueprint Step 11)

- **GDPR/CCPA**: data-export and account-deletion endpoints (cascade deletes already
  configured on the models); right-to-be-forgotten flows in cleanup playbooks.
- **Per-platform API limits**: add backoff/caching in `connectors/`; the `is_configured`
  + safe-wrapper pattern already isolates failures.
- **Model drift**: A/B the `llm` vs `rule_based` analyzers on the same corpus — both
  implement the identical interface, so swapping is a config flag.
