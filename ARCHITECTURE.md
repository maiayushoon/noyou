# NoYou — Architecture

NoYou implements the DRSP data-flow architecture as a set of swappable layers.
The guiding principle: **every external dependency sits behind an interface**, so the
product runs fully offline today and scales to real integrations with config changes.

```
┌──────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────────┐
│  User /  │   │  Connectors  │   │  Analyzers  │   │   Scoring    │
│ Accounts │──▶│ (data source │──▶│  (AI brain) │──▶│   engine     │
│          │   │   plugins)   │   │             │   │              │
└──────────┘   └──────────────┘   └─────────────┘   └──────┬───────┘
                                                            ▼
        ┌───────────────┐   ┌──────────┐   ┌────────────────────────┐
        │ Notifications │◀──│  Alerts  │◀──│  Dashboard / Reports   │
        └───────────────┘   └──────────┘   └────────────────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │ Cleanup tools │
                          └──────────────┘
```

## Layer map (diagram box → code)

| Architecture box | Module |
|------------------|--------|
| User Input / Connect Accounts | `models/account.py`, `api/routes/accounts.py` |
| Data Collection / Data Sources | `connectors/` (`base`, `demo`, `providers`, `registry`) |
| AI Analysis (sentiment, risk, context) | `analysis/` (`base`, `rule_based`, `llm`, `lexicon`) |
| Risk Assessment / Scoring | `services/scoring.py` |
| Dashboard & Alerts | `api/routes/dashboard.py`, `services/alerts.py` |
| Cleanup Tools / User Actions | `services/cleanup.py`, `api/routes/cleanup.py`, `mentions` status |
| Reports & Trends | `services/reports.py`, `api/routes/reports.py` |
| Notifications | `notifications/dispatcher.py` |
| Scheduled scanning (24/7) | `core/scheduler.py` + `services/scanning.py` |

## The two key interfaces

### `BaseConnector` (data sources)
```python
class BaseConnector(ABC):
    name: str
    def is_configured(self) -> bool: ...
    def search(self, query: str, *, limit: int = 25) -> list[RawMention]: ...
```
Add a source by writing one subclass and registering it in `connectors/registry.py`.
The registry only activates connectors whose credentials are present, and always
falls back to `DemoConnector` so a scan never returns nothing.

### `BaseAnalyzer` (AI)
```python
class BaseAnalyzer(ABC):
    name: str
    def analyze(self, item: AnalysisInput) -> AnalysisResult: ...
```
`RuleBasedAnalyzer` is the offline default. `LLMAnalyzer` calls OpenAI/Anthropic/HF
and **falls back to rule-based** on any error, so a missing key or quota never breaks
a scan. Selected via `ANALYZER` env var in `analysis/factory.py`.

## The scan pipeline (`services/scanning.py`)

1. Build search queries from the user's linked accounts (+ name fallback).
2. For each active connector × query → `search()` → `RawMention`s.
3. De-duplicate by `external_id` against existing mentions.
4. Persist each new `Mention`, run the analyzer → persist `Analysis`.
5. Generate `Alert`s (high-risk) and `CleanupAction`s (suggestions).
6. Recompute the reputation score over the user's whole corpus.
7. Dispatch notifications for high-severity alerts.

The same function is called by the **API** ("Run scan") and the **scheduler**
(automated 24/7 scans), guaranteeing identical behaviour.

## Data model

```
User 1───* Account
User 1───* Scan
User 1───* Mention 1───1 Analysis
                 │
                 ├──* Alert
                 └──* CleanupAction
```

IDs are cross-database UUIDs (`core/database.py:GUID`) — native UUID on Postgres,
CHAR(36) on SQLite — so the same code runs on either with no migration changes.

## Reputation scoring (`services/scoring.py`)

Extends the blueprint's algorithm with recency weighting (damage decays over a
~120-day half-life), positive-coverage lift (capped), and confidence weighting (the
AI moves the score less when it's unsure). Output is clamped to 0–100 and bucketed
into `low / medium / high / critical` bands.

## Security

- Passwords: bcrypt (`core/security.py`), 72-byte input handled.
- Auth: JWT bearer tokens (PyJWT), `get_current_user` dependency guards every route.
- Per-user data isolation: every query filters by `user_id`; ownership checked on
  mutations.
- CORS allow-list via `CORS_ORIGINS`.
- Secrets via environment only; nothing hard-coded.

## Where it scales next

- **Async scans**: replace the synchronous `run_scan` call in the API with a queued
  job (Celery / RQ / Cloud Tasks) — the function body is already a unit of work.
- **Connector concurrency**: `get_active_connectors()` returns a list; fan out with
  `asyncio`/threads when connectors are network-bound.
- **Vector search / RAG** over historical mentions for context understanding.
- See [ROADMAP.md](ROADMAP.md) for the full post-MVP plan mapped to these seams.
