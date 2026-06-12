from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ApiError, envelope
from app.models import User
from app.repositories.log_repo import WeightLogRepository
from app.schemas.logs import WeightLogCreate, WeightLogOut

router = APIRouter(prefix="/weight-logs", tags=["weight-logs"])


@router.get("")
def list_weight_logs(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = WeightLogRepository(db).list(
        user_id=user.id, date_from=date_from, date_to=date_to, limit=limit
    )
    return envelope([WeightLogOut.model_validate(log) for log in logs])


@router.post("")
def create_weight_log(
    data: WeightLogCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = WeightLogRepository(db).create(
        user_id=user.id, weight_kg=data.weight_kg, logged_at=data.logged_at
    )
    return envelope(WeightLogOut.model_validate(log), "Weight logged", 201)


@router.delete("/{log_id}")
def delete_weight_log(
    log_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WeightLogRepository(db)
    log = repo.get_by_id(log_id, user.id)
    if log is None:
        raise ApiError(404, "Weight log not found")
    repo.delete(log)
    return envelope(None, "Weight log deleted")
