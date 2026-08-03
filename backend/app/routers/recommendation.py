import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.event_service import EventService
from app.services.recommendation_service import RecommendationService, LOOKBACK_DAYS

router = APIRouter()


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendation(
    user_id: str,
    lookback_days: int = Query(default=LOOKBACK_DAYS, ge=1, le=365),
    event_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    event = EventService(db).get_event(event_id) if event_id else None
    if event_id and (event is None or event.user_id != user_id):
        raise HTTPException(status_code=404, detail="Event not found for this user")
    recommendation = service.generate_recommendation(user_id, lookback_days, event)
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail=f"No nudge history found for user '{user_id}' in the last {lookback_days} days",
        )
    return recommendation
