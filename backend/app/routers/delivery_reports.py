from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.delivery_report import DeliveryReportCreate, DeliveryReportRead
from app.services.nudge_service import NudgeService

router = APIRouter()


@router.post("", response_model=DeliveryReportRead, status_code=201)
def submit_delivery_report(report_in: DeliveryReportCreate, db: Session = Depends(get_db)):
    service = NudgeService(db)
    nudge = service.get_nudge(report_in.nudge_id)
    if not nudge:
        raise HTTPException(status_code=404, detail="Referenced nudge not found")
    return service.submit_delivery_report(report_in)
