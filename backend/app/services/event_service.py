import uuid

from sqlalchemy.orm import Session

from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate


class EventService:
    def __init__(self, db: Session):
        self.repo = EventRepository(db)

    def create_event(self, event_in: EventCreate):
        return self.repo.create(event_in)

    def list_events(self, user_id: str | None = None, skip: int = 0, limit: int = 100):
        return self.repo.list(user_id=user_id, skip=skip, limit=limit)

    def get_event(self, event_id: uuid.UUID):
        return self.repo.get_by_id(event_id)
