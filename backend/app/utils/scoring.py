"""Engagement scoring utilities."""

from datetime import datetime, timezone

ENGAGEMENT_SCORES = {
    "REPLIED": 5,
    "CLICKED": 3,
    "OPENED": 2,
    "DELIVERED": 1,
    "FAILED": -3,
}


def engagement_score(status: str) -> int:
    return ENGAGEMENT_SCORES.get(status, 0)


def recency_weight(sent_time: datetime, now: datetime | None = None) -> float:
    """weight = 1 / (days_old + 1)"""
    if now is None:
        now = datetime.now(timezone.utc)

    if sent_time.tzinfo is None:
        sent_time = sent_time.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    days_old = max((now - sent_time).total_seconds() / 86400.0, 0.0)
    return 1.0 / (days_old + 1.0)


def weighted_score(status: str, sent_time: datetime, now: datetime | None = None) -> float:
    return engagement_score(status) * recency_weight(sent_time, now)


MIN_OBSERVATIONS_FOR_HIGH_CONFIDENCE = 5
MAX_HEURISTIC_CONFIDENCE = 0.95


def normalize_confidence(scores: list[float], observation_count: int) -> float:
    """Return a calibrated confidence for a heuristic recommendation.

    A clear winning time bucket alone is not enough to claim certainty: a
    single positive nudge would otherwise yield 100%. The score distribution
    is therefore scaled by the amount of observed history and capped below
    100% because this is not a probabilistic model.
    """
    if not scores:
        return 0.0
    total = sum(abs(s) for s in scores)
    if total == 0:
        return 0.0
    best = max(scores)
    distribution_confidence = best / total
    evidence_factor = min(
        max(observation_count, 0) / MIN_OBSERVATIONS_FOR_HIGH_CONFIDENCE, 1.0
    )
    confidence = distribution_confidence * evidence_factor
    return max(0.0, min(round(confidence, 2), MAX_HEURISTIC_CONFIDENCE))
