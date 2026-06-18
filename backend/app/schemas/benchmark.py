from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CompetitorIn(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="Competitor name or brand to benchmark against")


class CompetitorOut(BaseModel):
    id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SentimentCounts(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class BenchmarkEntry(BaseModel):
    name: str
    is_you: bool = False
    reputation_score: float
    band: str
    total_mentions: int
    sentiment: SentimentCounts


class BenchmarkReport(BaseModel):
    generated_at: str
    entries: list[BenchmarkEntry]
