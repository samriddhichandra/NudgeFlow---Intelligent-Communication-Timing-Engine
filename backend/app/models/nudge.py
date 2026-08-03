import enum
import uuid

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class NudgeChannel(str, enum.Enum):
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class NudgeStatus(str, enum.Enum):
    DELIVERED = "DELIVERED"
    OPENED = "OPENED"
    CLICKED = "CLICKED"
    REPLIED = "REPLIED"
    FAILED = "FAILED"


class Nudge(Base):
    __tablename__ = "nudges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    channel = Column(Enum(NudgeChannel), nullable=False)
    sent_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(NudgeStatus), nullable=False, default=NudgeStatus.DELIVERED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
