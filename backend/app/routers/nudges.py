import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.nudge import NudgeCreate, NudgeRead
from app.services.nudge_service import NudgeService

router = APIRouter()


@router.post("", response_model=NudgeRead, status_code=201)
def create_nudge(nudge_in: NudgeCreate, db: Session = Depends(get_db)):
    service = NudgeService(db)
    return service.create_nudge(nudge_in)


@router.get("", response_model=list[NudgeRead])
def list_nudges(
    user_id: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    service = NudgeService(db)
    return service.list_nudges(user_id=user_id, skip=skip, limit=limit)


@router.get("/{nudge_id}", response_model=NudgeRead)
def get_nudge(nudge_id: uuid.UUID, db: Session = Depends(get_db)):
    service = NudgeService(db)
    nudge = service.get_nudge(nudge_id)
    if not nudge:
        raise HTTPException(status_code=404, detail="Nudge not found")
    return nudge
