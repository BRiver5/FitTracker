from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ApiError, envelope
from app.models import User
from app.repositories.log_repo import CalorieLogRepository
from app.schemas.logs import CalorieLogCreate, CalorieLogOut

router = APIRouter(prefix="/calorie-logs", tags=["calorie-logs"])


@router.get("")
def list_calorie_logs(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = CalorieLogRepository(db).list(user_id=user.id, date_from=date_from, date_to=date_to)
    return envelope([CalorieLogOut.model_validate(log) for log in logs])


@router.post("")
def create_calorie_log(
    data: CalorieLogCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = data.model_dump()
    logged_at = payload.pop("logged_at")
    log = CalorieLogRepository(db).create(user_id=user.id, logged_at=logged_at, **payload)
    return envelope(CalorieLogOut.model_validate(log), "Food logged", 201)


@router.delete("/{log_id}")
def delete_calorie_log(
    log_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CalorieLogRepository(db)
    log = repo.get_by_id(log_id, user.id)
    if log is None:
        raise ApiError(404, "Calorie log not found")
    repo.delete(log)
    return envelope(None, "Calorie log deleted")
