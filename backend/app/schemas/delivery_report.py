import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.nudge import NudgeStatus


class DeliveryReportCreate(BaseModel):
    nudge_id: uuid.UUID
    status: NudgeStatus
    meta: Optional[str] = None


class DeliveryReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nudge_id: uuid.UUID
    status: str
    report_time: datetime
    meta: Optional[str] = None
