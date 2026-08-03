from datetime import datetime
from typing import Dict
import uuid

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    user_id: str
    event_id: uuid.UUID | None = None
    recommended_time: datetime
    channel: str
    confidence: float
    reason: str


class BucketScore(BaseModel):
    bucket: str
    score: float
    count: int


class ChannelScore(BaseModel):
    channel: str
    score: float
    count: int


class AnalyticsResponse(BaseModel):
    user_id: str
    engagement_by_bucket: Dict[str, float]
    engagement_by_channel: Dict[str, float]
    total_nudges: int
    recommendation: RecommendationResponse | None = None
