import uuid

from sqlalchemy.orm import Session

from app.models.nudge import Nudge, NudgeStatus
from app.models.delivery_report import DeliveryReport
from app.schemas.nudge import NudgeCreate
from app.schemas.delivery_report import DeliveryReportCreate


class NudgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, nudge_in: NudgeCreate) -> Nudge:
        nudge = Nudge(**nudge_in.model_dump())
        self.db.add(nudge)
        self.db.commit()
        self.db.refresh(nudge)
        return nudge

    def list(self, user_id: str | None = None, skip: int = 0, limit: int = 200) -> list[Nudge]:
        query = self.db.query(Nudge)
        if user_id:
            query = query.filter(Nudge.user_id == user_id)
        return query.order_by(Nudge.sent_time.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, nudge_id: uuid.UUID) -> Nudge | None:
        return self.db.query(Nudge).filter(Nudge.id == nudge_id).first()

    def list_for_user_since(self, user_id: str, since):
        return (
            self.db.query(Nudge)
            .filter(Nudge.user_id == user_id, Nudge.sent_time >= since)
            .all()
        )

    def create_delivery_report(self, report_in: DeliveryReportCreate) -> DeliveryReport:
        report = DeliveryReport(**report_in.model_dump())
        self.db.add(report)

        nudge = self.get_by_id(report_in.nudge_id)
        if nudge is not None and self._should_update_status(nudge.status, report_in.status):
            nudge.status = report_in.status

        self.db.commit()
        self.db.refresh(report)
        return report

    @staticmethod
    def _should_update_status(current: NudgeStatus, incoming: NudgeStatus) -> bool:
        """Keep the strongest observed engagement when provider reports arrive late."""
        rank = {
            NudgeStatus.FAILED: 0,
            NudgeStatus.DELIVERED: 1,
            NudgeStatus.OPENED: 2,
            NudgeStatus.CLICKED: 3,
            NudgeStatus.REPLIED: 4,
        }
        return rank[incoming] >= rank[current]
