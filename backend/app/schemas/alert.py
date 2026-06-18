from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    is_read: bool
    mention_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
