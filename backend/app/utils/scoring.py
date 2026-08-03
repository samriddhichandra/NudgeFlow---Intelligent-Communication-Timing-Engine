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


def normalize_confidence(scores: list[float]) -> float:
    """Normalize the winning score against the total absolute magnitude of
    all scores to produce a 0-1 confidence value."""
    if not scores:
        return 0.0
    total = sum(abs(s) for s in scores)
    if total == 0:
        return 0.0
    best = max(scores)
    confidence = best / total
    return max(0.0, min(round(confidence, 2), 1.0))
