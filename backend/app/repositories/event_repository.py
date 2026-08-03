import uuid

from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventCreate


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event_in: EventCreate) -> Event:
        event = Event(**event_in.model_dump())
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list(self, user_id: str | None = None, skip: int = 0, limit: int = 100) -> list[Event]:
        query = self.db.query(Event)
        if user_id:
            query = query.filter(Event.user_id == user_id)
        return query.order_by(Event.event_time.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, event_id: uuid.UUID) -> Event | None:
        return self.db.query(Event).filter(Event.id == event_id).first()
