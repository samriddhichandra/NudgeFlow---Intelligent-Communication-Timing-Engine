import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class DeliveryReport(Base):
    __tablename__ = "delivery_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nudge_id = Column(UUID(as_uuid=True), ForeignKey("nudges.id"), nullable=False)
    status = Column(String, nullable=False)
    report_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    meta = Column(String, nullable=True)
