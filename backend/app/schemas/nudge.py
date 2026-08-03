import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.nudge import NudgeChannel, NudgeStatus


class NudgeCreate(BaseModel):
    user_id: str
    channel: NudgeChannel
    sent_time: datetime
    status: NudgeStatus = NudgeStatus.DELIVERED


class NudgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    channel: NudgeChannel
    sent_time: datetime
    status: NudgeStatus
    created_at: datetime
