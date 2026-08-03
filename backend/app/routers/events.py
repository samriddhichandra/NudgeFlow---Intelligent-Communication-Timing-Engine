import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import EventCreate, EventRead
from app.services.event_service import EventService
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService, LOOKBACK_DAYS

router = APIRouter()


@router.post("", response_model=EventRead, status_code=201)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    service = EventService(db)
    return service.create_event(event_in)


@router.get("", response_model=list[EventRead])
def list_events(
    user_id: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = EventService(db)
    return service.list_events(user_id=user_id, skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    service = EventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/recommendation", response_model=RecommendationResponse)
def get_event_recommendation(
    event_id: uuid.UUID,
    lookback_days: int = Query(default=LOOKBACK_DAYS, ge=1, le=365),
    db: Session = Depends(get_db),
):
    event = EventService(db).get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return RecommendationService(db).generate_recommendation(
        event.user_id, lookback_days, event
    )
