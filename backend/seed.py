"""Seed the database with sample events and nudge history for demo purposes.

Usage (inside the backend container or a local venv with DATABASE_URL set):
    python seed.py
"""

import random
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal, Base, engine
from app.models.event import Event, EventPriority
from app.models.nudge import Nudge, NudgeChannel, NudgeStatus

random.seed(42)

USERS = ["user_001", "user_002", "user_003"]
EVENT_TYPES = ["signup", "cart_abandon", "renewal_due", "support_ticket", "milestone"]
CHANNELS = list(NudgeChannel)
STATUSES = list(NudgeStatus)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # Clear existing demo data (idempotent-ish for local dev)
        db.query(Nudge).delete()
        db.query(Event).delete()
        db.commit()

        for user_id in USERS:
            # A handful of events per user
            for _ in range(5):
                db.add(
                    Event(
                        user_id=user_id,
                        event_type=random.choice(EVENT_TYPES),
                        event_time=now - timedelta(days=random.randint(0, 25)),
                        priority=random.choice(list(EventPriority)),
                    )
                )

            # user_001: strong evening WhatsApp engagement
            if user_id == "user_001":
                for i in range(8):
                    sent = now - timedelta(days=random.randint(0, 25), hours=-random.randint(18, 20))
                    db.add(
                        Nudge(
                            user_id=user_id,
                            channel=NudgeChannel.WHATSAPP,
                            sent_time=now - timedelta(days=random.randint(0, 20))
                            .replace(),
                            status=random.choice(
                                [NudgeStatus.REPLIED, NudgeStatus.CLICKED, NudgeStatus.REPLIED]
                            ),
                        )
                    )
                # fix sent_time to be within 6-9pm bucket
                for n in db.query(Nudge).filter(Nudge.user_id == user_id).all():
                    days_old = random.randint(0, 20)
                    n.sent_time = (now - timedelta(days=days_old)).replace(
                        hour=19, minute=random.randint(0, 59)
                    )
                # add some noise on other channels/times with weaker engagement
                for _ in range(4):
                    days_old = random.randint(0, 25)
                    db.add(
                        Nudge(
                            user_id=user_id,
                            channel=random.choice([NudgeChannel.EMAIL, NudgeChannel.SMS]),
                            sent_time=(now - timedelta(days=days_old)).replace(hour=10),
                            status=random.choice([NudgeStatus.DELIVERED, NudgeStatus.FAILED]),
                        )
                    )

            # user_002: morning email engagement
            elif user_id == "user_002":
                for _ in range(7):
                    days_old = random.randint(0, 20)
                    db.add(
                        Nudge(
                            user_id=user_id,
                            channel=NudgeChannel.EMAIL,
                            sent_time=(now - timedelta(days=days_old)).replace(
                                hour=random.choice([6, 7, 8])
                            ),
                            status=random.choice(
                                [NudgeStatus.OPENED, NudgeStatus.CLICKED, NudgeStatus.OPENED]
                            ),
                        )
                    )
                for _ in range(3):
                    days_old = random.randint(0, 25)
                    db.add(
                        Nudge(
                            user_id=user_id,
                            channel=random.choice([NudgeChannel.PUSH, NudgeChannel.SMS]),
                            sent_time=(now - timedelta(days=days_old)).replace(hour=15),
                            status=NudgeStatus.FAILED,
                        )
                    )

            # user_003: sparse / mixed engagement (low confidence case)
            else:
                for _ in range(4):
                    days_old = random.randint(0, 29)
                    db.add(
                        Nudge(
                            user_id=user_id,
                            channel=random.choice(CHANNELS),
                            sent_time=(now - timedelta(days=days_old)).replace(
                                hour=random.randint(6, 23)
                            ),
                            status=random.choice(STATUSES),
                        )
                    )

        db.commit()
        print("Seed data created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
