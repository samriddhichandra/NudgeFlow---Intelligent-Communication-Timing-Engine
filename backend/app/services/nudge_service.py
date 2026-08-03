import uuid

from sqlalchemy.orm import Session

from app.repositories.nudge_repository import NudgeRepository
from app.schemas.nudge import NudgeCreate
from app.schemas.delivery_report import DeliveryReportCreate


class NudgeService:
    def __init__(self, db: Session):
        self.repo = NudgeRepository(db)

    def create_nudge(self, nudge_in: NudgeCreate):
        return self.repo.create(nudge_in)

    def list_nudges(self, user_id: str | None = None, skip: int = 0, limit: int = 200):
        return self.repo.list(user_id=user_id, skip=skip, limit=limit)

    def get_nudge(self, nudge_id: uuid.UUID):
        return self.repo.get_by_id(nudge_id)

    def submit_delivery_report(self, report_in: DeliveryReportCreate):
        return self.repo.create_delivery_report(report_in)
