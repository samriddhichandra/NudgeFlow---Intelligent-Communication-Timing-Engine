import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.event import EventPriority


class EventCreate(BaseModel):
    user_id: str
    event_type: str
    event_time: datetime
    priority: EventPriority = EventPriority.MEDIUM


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    event_type: str
    event_time: datetime
    priority: EventPriority
    created_at: datetime
