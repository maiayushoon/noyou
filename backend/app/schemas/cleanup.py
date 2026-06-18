from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CleanupActionOut(BaseModel):
    id: str
    mention_id: str
    action_type: str
    title: str
    instructions: str
    status: str
    automated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CleanupStatusUpdate(BaseModel):
    status: str  # suggested | in_progress | completed | dismissed
