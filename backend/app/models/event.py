import enum
import uuid

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class EventPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    priority = Column(Enum(EventPriority), nullable=False, default=EventPriority.MEDIUM)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
