"""Core recommendation engine.

Builds time-bucket and channel engagement scores from a user's nudge
history, applies recency weighting, and produces a recommendation for
the best time and channel to send the next nudge.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.nudge_repository import NudgeRepository
from app.models.nudge import Nudge
from app.models.event import Event
from app.schemas.recommendation import RecommendationResponse
from app.utils.time_buckets import (
    TIME_BUCKETS,
    get_bucket_for_time,
    next_datetime_for_bucket,
    next_safe_nudge_time,
)
from app.utils.scoring import weighted_score, normalize_confidence

LOOKBACK_DAYS = 30
DEFAULT_CHANNEL = "WHATSAPP"


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NudgeRepository(db)

    def _lookback_nudges(self, user_id: str, lookback_days: int = LOOKBACK_DAYS) -> list[Nudge]:
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        return self.repo.list_for_user_since(user_id, since)

    def _bucket_scores(self, nudges: list[Nudge], now: datetime) -> dict[str, dict]:
        scores: dict[str, dict] = {
            b.key: {"score": 0.0, "count": 0} for b in TIME_BUCKETS
        }
        for nudge in nudges:
            bucket = get_bucket_for_time(nudge.sent_time)
            ws = weighted_score(nudge.status.value, nudge.sent_time, now)
            scores[bucket.key]["score"] += ws
            scores[bucket.key]["count"] += 1
        return scores

    def _channel_scores(self, nudges: list[Nudge], now: datetime) -> dict[str, dict]:
        scores: dict[str, dict] = defaultdict(lambda: {"score": 0.0, "count": 0})
        for nudge in nudges:
            channel = nudge.channel.value
            ws = weighted_score(nudge.status.value, nudge.sent_time, now)
            scores[channel]["score"] += ws
            scores[channel]["count"] += 1
        return dict(scores)

    def _build_reason(
        self,
        user_id: str,
        best_bucket_key: str,
        best_channel: str,
        nudges: list[Nudge],
        lookback_days: int,
    ) -> str:
        bucket = next(b for b in TIME_BUCKETS if b.key == best_bucket_key)

        # Find the dominant engagement action for this bucket/channel combo,
        # preferring the strongest positive signal (REPLIED > CLICKED > OPENED > DELIVERED).
        priority = ["REPLIED", "CLICKED", "OPENED", "DELIVERED"]
        counts = defaultdict(int)
        for nudge in nudges:
            if (
                get_bucket_for_time(nudge.sent_time).key == best_bucket_key
                and nudge.channel.value == best_channel
            ):
                counts[nudge.status.value] += 1

        dominant_status = None
        for status in priority:
            if counts.get(status, 0) > 0:
                dominant_status = status
                break

        if dominant_status is None:
            return (
                f"Not enough recent engagement data for user {user_id}; "
                f"defaulting to the best available window, {bucket.label}, on {best_channel}."
            )

        verb_map = {
            "REPLIED": "replied to",
            "CLICKED": "clicked",
            "OPENED": "opened",
            "DELIVERED": "received (but not yet engaged with)",
        }
        count = counts[dominant_status]
        return (
            f"User has {verb_map[dominant_status]} {count} {best_channel.title()} "
            f"nudge{'s' if count != 1 else ''} between {bucket.label} during the last "
            f"{lookback_days} days."
        )

    @staticmethod
    def _utc(dt: datetime) -> datetime:
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)

    def generate_recommendation(
        self,
        user_id: str,
        lookback_days: int = LOOKBACK_DAYS,
        event: Event | None = None,
    ) -> RecommendationResponse | None:
        now = datetime.now(timezone.utc)
        nudges = self._lookback_nudges(user_id, lookback_days)

        if not nudges:
            if event is None:
                return None
            reference = max(now, self._utc(event.event_time))
            bucket, recommended_time = next_safe_nudge_time(reference)
            return RecommendationResponse(
                user_id=user_id,
                event_id=event.id,
                recommended_time=recommended_time,
                channel=DEFAULT_CHANNEL,
                confidence=0.0,
                reason=(
                    f"No recent nudge history is available for this {event.event_type} event; "
                    f"schedule a default {DEFAULT_CHANNEL.title()} nudge in the next safe "
                    f"window ({bucket.label})."
                ),
            )

        bucket_scores = self._bucket_scores(nudges, now)
        channel_scores = self._channel_scores(nudges, now)

        eligible_buckets = [b.key for b in TIME_BUCKETS if b.key != "12AM-6AM"]
        best_bucket_key = max(eligible_buckets, key=lambda k: bucket_scores[k]["score"])
        best_bucket = next(b for b in TIME_BUCKETS if b.key == best_bucket_key)

        positive_channels = {
            channel: values for channel, values in channel_scores.items() if values["score"] > 0
        }
        if positive_channels:
            best_channel = max(positive_channels, key=lambda k: positive_channels[k]["score"])
        else:
            best_channel = DEFAULT_CHANNEL

        confidence = normalize_confidence(
            [bucket_scores[k]["score"] for k in eligible_buckets if bucket_scores[k]["count"] > 0]
        )

        reference = max(now, self._utc(event.event_time)) if event else now
        recommended_time = next_datetime_for_bucket(best_bucket, reference)

        reason = self._build_reason(
            user_id, best_bucket_key, best_channel, nudges, lookback_days
        )

        return RecommendationResponse(
            user_id=user_id,
            event_id=event.id if event else None,
            recommended_time=recommended_time,
            channel=best_channel,
            confidence=confidence,
            reason=reason,
        )
