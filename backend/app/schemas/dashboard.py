from __future__ import annotations

from pydantic import BaseModel

from .alert import AlertOut
from .mention import MentionOut


class ScoreTrendPoint(BaseModel):
    """One point on the hero sparkline: a completed scan's score_after at a date."""

    date: str
    score: float


class DashboardSummary(BaseModel):
    reputation_score: float
    band: str
    total_mentions: int
    sentiment_counts: dict[str, int]
    high_risk_count: int
    unread_alerts: int
    active_cleanup_actions: int
    last_scan_at: str | None = None
    # Change from the most recent completed scan: score_after - score_before.
    # 0.0 when there is no prior scan; previous_score is that scan's score_before.
    score_delta: float = 0.0
    previous_score: float | None = None
    # Up-to-8 most recent completed-scan scores, oldest -> newest, for a sparkline.
    score_trend: list[ScoreTrendPoint] = []
    top_alerts: list[AlertOut] = []
    recent_high_risk: list[MentionOut] = []
