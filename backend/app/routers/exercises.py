from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import envelope
from app.models import User
from app.repositories.exercise_repo import ExerciseRepository
from app.schemas.workout import ExerciseCreate, ExerciseOut

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("")
def list_exercises(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    muscle: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercises = ExerciseRepository(db).list(
        user_id=user.id, search=search, category=category, muscle=muscle
    )
    return envelope([ExerciseOut.model_validate(e) for e in exercises])


@router.post("")
def create_exercise(
    data: ExerciseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseRepository(db).create(user_id=user.id, **data.model_dump())
    return envelope(ExerciseOut.model_validate(exercise), "Exercise created", 201)
