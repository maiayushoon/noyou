from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ScanOut(BaseModel):
    id: str
    status: str
    trigger: str
    connectors_used: str | None = None
    mentions_found: int
    new_mentions: int
    score_before: float | None = None
    score_after: float | None = None
    error: str | None = None
    started_at: datetime
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}
