from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendation import AnalyticsResponse
from app.services.analytics_service import AnalyticsService
from app.services.recommendation_service import LOOKBACK_DAYS

router = APIRouter()


@router.get("/{user_id}/analytics", response_model=AnalyticsResponse)
def get_user_analytics(
    user_id: str,
    lookback_days: int = Query(default=LOOKBACK_DAYS, ge=1, le=365),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return service.get_analytics(user_id, lookback_days)
