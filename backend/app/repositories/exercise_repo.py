from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Exercise


class ExerciseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, exercise_id: int) -> Exercise | None:
        return self.db.get(Exercise, exercise_id)

    def list(
        self,
        *,
        user_id: int,
        search: str | None = None,
        category: str | None = None,
        muscle: str | None = None,
    ) -> list[Exercise]:
        query = select(Exercise).where(
            or_(Exercise.is_default.is_(True), Exercise.created_by_user_id == user_id)
        )
        if search:
            query = query.where(Exercise.name.ilike(f"%{search}%"))
        if category:
            query = query.where(func.lower(Exercise.category) == category.lower())
        results = list(self.db.scalars(query.order_by(Exercise.name)))
        if muscle:
            needle = muscle.lower()
            results = [e for e in results if any(needle in m.lower() for m in e.muscle_groups)]
        return results

    def create(self, *, user_id: int, **fields) -> Exercise:
        exercise = Exercise(created_by_user_id=user_id, is_default=False, **fields)
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def count_defaults(self) -> int:
        return self.db.scalar(select(func.count(Exercise.id)).where(Exercise.is_default.is_(True))) or 0
