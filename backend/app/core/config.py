"""Application configuration.

All settings are read from the environment (or a `.env` file) with safe defaults,
so the product runs end-to-end with an empty configuration. See `.env.example`.
"""
from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Placeholder secrets that must never be used to sign real tokens.
_DEFAULT_SECRETS = {"", "change-me-in-production", "dev-secret-change-me"}
_MIN_SECRET_LEN = 32

# Anchor the .env to backend/.env (this file is backend/app/core/config.py) so it
# loads the same regardless of the working directory the app is launched from.
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Project ---
    project_name: str = "NoYou"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"      # development | production
    frontend_url: str = "http://localhost:8000"

    # --- Database ---
    database_url: str = "sqlite:///./noyou.db"

    # --- Auth / security ---
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Public-signup email flows
    require_email_verification: bool = False
    email_token_expire_hours: int = 24
    reset_token_expire_hours: int = 2

    # Rate limiting (requests per minute, per client IP)
    rate_limit_per_minute: int = 60
    auth_rate_limit_per_minute: int = 10

    # --- CORS ---
    cors_origins: str = "http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000"

    # --- AI analysis ---
    analyzer: str = "rule_based"          # rule_based | trained | llm
    llm_provider: str = "openai"          # openai | anthropic | huggingface
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    huggingface_api_key: str = ""

    # Directory holding the trained sentiment model (sentiment.joblib). Empty =>
    # the package's app/ml/models/ dir. Set this to mount a model in production.
    ml_model_dir: str = ""

    # --- Connectors ---
    connectors: str = "demo"              # comma list: demo,google,twitter,...
    google_api_key: str = ""
    google_cse_id: str = ""
    twitter_bearer_token: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "noyou/1.0"
    youtube_api_key: str = ""

    # --- OAuth account-linking (Connections) ---
    # Tokens for the user's OWN accounts, stored encrypted. Distinct from the
    # keyless/public connectors above (e.g. GOOGLE_API_KEY, REDDIT_CLIENT_ID).
    # Each redirect URI must be {FRONTEND_URL}/api/v1/connections/{provider}/callback.
    # Mastodon needs NO global credentials — it self-registers per instance.
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    reddit_oauth_client_id: str = ""
    reddit_oauth_client_secret: str = ""
    threads_app_id: str = ""
    threads_app_secret: str = ""
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    mastodon_app_name: str = "NoYou"
    # Optional Fernet key override decoupling token encryption from SECRET_KEY
    # (urlsafe-base64 32 bytes). Empty => key is derived from SECRET_KEY.
    token_encryption_key: str = ""
    # Public base URL of THIS backend (where the OAuth callback lives), e.g.
    # https://api.noyou.app. The provider redirect_uri is built from this, NOT
    # FRONTEND_URL. Empty => auto-detected from the incoming request's origin.
    oauth_callback_base_url: str = ""

    # Drop fuzzy-junk mentions whose text isn't actually about the search
    # subject (broad keyless sources match "precourt"/"prcount"/"court"/...).
    # When False, keep all mentions (old, pre-filter behavior).
    relevance_filter: bool = True

    # --- Background scanning ---
    scan_interval_minutes: int = 360

    # --- Weekly digest email ---
    # Master switch for the scheduled weekly reputation digest. When False the
    # job is not registered and send_weekly_digests is a no-op.
    digest_enabled: bool = True
    # Day of week the digest runs, 0 = Monday .. 6 = Sunday (APScheduler cron).
    weekly_digest_day: int = 0
    # Hour of day (0-23, server local time) the digest runs.
    weekly_digest_hour: int = 8

    # --- Demo seeding ---
    seed_demo: bool = True
    demo_email: str = "demo@noyou.app"
    demo_password: str = "demo12345"

    # --- Notifications ---
    notify_channel: str = "console"       # console | email | resend
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "alerts@noyou.app"
    resend_api_key: str = ""              # https://resend.com — easiest production email

    # --- Stripe billing ---
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_premium: str = ""
    stripe_price_enterprise: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def connector_list(self) -> list[str]:
        return [c.strip().lower() for c in self.connectors.split(",") if c.strip()]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    # Never sign tokens with a shipped/placeholder secret.
    #  - development: auto-generate a strong ephemeral key (zero-config local runs
    #    still work; tokens simply reset on restart, and no public key is trusted).
    #  - anything else (production/staging): refuse to boot until a strong, unique
    #    SECRET_KEY is provided. This fails CLOSED, so a deploy that forgets to set
    #    the secret crashes loudly instead of silently trusting a repo-published key.
    weak = s.secret_key in _DEFAULT_SECRETS or "change" in s.secret_key.lower()
    if s.environment == "development":
        if weak:
            s.secret_key = secrets.token_urlsafe(48)
    else:
        if weak or len(s.secret_key) < _MIN_SECRET_LEN:
            raise RuntimeError(
                "Refusing to start: SECRET_KEY must be a strong, unique value "
                f"(>= {_MIN_SECRET_LEN} chars) when ENVIRONMENT is not 'development'. "
                'Generate one with: python -c "import secrets;print(secrets.token_hex(32))"'
            )
    return s


settings = get_settings()
