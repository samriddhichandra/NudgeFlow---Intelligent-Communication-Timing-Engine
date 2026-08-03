"""Time bucket definitions and helpers.

Buckets are defined by hour-of-day ranges (24h clock, local/naive time
of the sent_time as stored):

    6AM-9AM   -> 06:00 - 08:59
    9AM-12PM  -> 09:00 - 11:59
    12PM-3PM  -> 12:00 - 14:59
    3PM-6PM   -> 15:00 - 17:59
    6PM-9PM   -> 18:00 - 20:59
    9PM-12AM  -> 21:00 - 23:59

Anything outside 6AM-12AM (i.e. midnight to 6AM) falls into the
"12AM-6AM" bucket for completeness, though it is not part of the
core business-defined buckets.
"""

from datetime import datetime, timedelta
from typing import NamedTuple


class TimeBucket(NamedTuple):
    key: str
    label: str
    start_hour: int
    end_hour: int  # exclusive
    representative_hour: int  # hour used to build a recommended datetime


TIME_BUCKETS: list[TimeBucket] = [
    TimeBucket("6AM-9AM", "6 AM - 9 AM", 6, 9, 7),
    TimeBucket("9AM-12PM", "9 AM - 12 PM", 9, 12, 10),
    TimeBucket("12PM-3PM", "12 PM - 3 PM", 12, 15, 13),
    TimeBucket("3PM-6PM", "3 PM - 6 PM", 15, 18, 16),
    TimeBucket("6PM-9PM", "6 PM - 9 PM", 18, 21, 19),
    TimeBucket("9PM-12AM", "9 PM - 12 AM", 21, 24, 22),
    TimeBucket("12AM-6AM", "12 AM - 6 AM", 0, 6, 2),
]

BUCKET_BY_KEY = {b.key: b for b in TIME_BUCKETS}


def get_bucket_for_time(dt: datetime) -> TimeBucket:
    hour = dt.hour
    for bucket in TIME_BUCKETS:
        if bucket.start_hour <= hour < bucket.end_hour:
            return bucket
    return TIME_BUCKETS[-1]


def next_datetime_for_bucket(bucket: TimeBucket, reference: datetime) -> datetime:
    """Return the next occurrence (today or tomorrow) of the bucket's
    representative hour, relative to `reference`."""
    candidate = reference.replace(
        hour=bucket.representative_hour, minute=0, second=0, microsecond=0
    )
    if candidate <= reference:
        candidate = candidate + timedelta(days=1)
    return candidate


def next_safe_nudge_time(reference: datetime) -> tuple[TimeBucket, datetime]:
    """Return a near-term default that never sends in the overnight window."""
    current_bucket = get_bucket_for_time(reference)
    if current_bucket.key != "12AM-6AM":
        return current_bucket, reference.replace(second=0, microsecond=0) + timedelta(minutes=5)

    morning = BUCKET_BY_KEY["9AM-12PM"]
    candidate = reference.replace(hour=9, minute=0, second=0, microsecond=0)
    if candidate <= reference:
        candidate += timedelta(days=1)
    return morning, candidate
