from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services.recommendation_service import RecommendationService, LOOKBACK_DAYS
from app.schemas.recommendation import AnalyticsResponse


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.rec_service = RecommendationService(db)

    def get_analytics(self, user_id: str, lookback_days: int = LOOKBACK_DAYS) -> AnalyticsResponse:
        now = datetime.now(timezone.utc)
        nudges = self.rec_service._lookback_nudges(user_id, lookback_days)

        bucket_scores = self.rec_service._bucket_scores(nudges, now)
        channel_scores = self.rec_service._channel_scores(nudges, now)

        engagement_by_bucket = {k: round(v["score"], 3) for k, v in bucket_scores.items()}
        engagement_by_channel = {k: round(v["score"], 3) for k, v in channel_scores.items()}

        recommendation = self.rec_service.generate_recommendation(user_id, lookback_days)

        return AnalyticsResponse(
            user_id=user_id,
            engagement_by_bucket=engagement_by_bucket,
            engagement_by_channel=engagement_by_channel,
            total_nudges=len(nudges),
            recommendation=recommendation,
        )
