from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import envelope
from app.models import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

RANGE_DAYS = {"week": 7, "month": 30, "3months": 90, "year": 365}


@router.get("/summary")
def get_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return envelope(AnalyticsService(db).summary(user.id))


@router.get("/progress")
def get_progress(
    range: str = Query(default="week", pattern="^(week|month|3months|year)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return envelope(AnalyticsService(db).progress(user.id, RANGE_DAYS[range]))
