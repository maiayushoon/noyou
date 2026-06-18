from __future__ import annotations

from pydantic import BaseModel

from .alert import AlertOut
from .mention import MentionOut


class DashboardSummary(BaseModel):
    reputation_score: float
    band: str
    total_mentions: int
    sentiment_counts: dict[str, int]
    high_risk_count: int
    unread_alerts: int
    active_cleanup_actions: int
    last_scan_at: str | None = None
    top_alerts: list[AlertOut] = []
    recent_high_risk: list[MentionOut] = []
