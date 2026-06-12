from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ApiError, envelope
from app.models import User
from app.repositories.plan_repo import WorkoutPlanRepository
from app.schemas.workout import WorkoutPlanCreate, WorkoutPlanOut, WorkoutPlanUpdate

router = APIRouter(prefix="/workout-plans", tags=["workout-plans"])


@router.get("")
def list_plans(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sort: str = Query(default="recent"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plans = WorkoutPlanRepository(db).list(
        user_id=user.id, search=search, category=category, sort=sort
    )
    return envelope([WorkoutPlanOut.model_validate(p) for p in plans])


@router.post("")
def create_plan(
    data: WorkoutPlanCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = WorkoutPlanRepository(db).create(
        user_id=user.id,
        name=data.name,
        description=data.description,
        category=data.category,
        schedule=data.schedule,
        exercises=data.exercises,
    )
    return envelope(WorkoutPlanOut.model_validate(plan), "Workout plan created", 201)


@router.get("/{plan_id}")
def get_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = WorkoutPlanRepository(db).get_by_id(plan_id, user.id)
    if plan is None:
        raise ApiError(404, "Workout plan not found")
    return envelope(WorkoutPlanOut.model_validate(plan))


@router.put("/{plan_id}")
def update_plan(
    plan_id: int,
    data: WorkoutPlanUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkoutPlanRepository(db)
    plan = repo.get_by_id(plan_id, user.id)
    if plan is None:
        raise ApiError(404, "Workout plan not found")
    fields = data.model_dump(exclude_unset=True, exclude={"exercises"})
    updated = repo.update(plan, fields, data.exercises)
    return envelope(WorkoutPlanOut.model_validate(updated), "Workout plan updated")


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkoutPlanRepository(db)
    plan = repo.get_by_id(plan_id, user.id)
    if plan is None:
        raise ApiError(404, "Workout plan not found")
    repo.delete(plan)
    return envelope(None, "Workout plan deleted")
