from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import WorkoutPlan, WorkoutPlanExercise
from app.schemas.workout import PlanExerciseIn


class WorkoutPlanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return select(WorkoutPlan).options(
            selectinload(WorkoutPlan.exercises).selectinload(WorkoutPlanExercise.exercise)
        )

    def get_by_id(self, plan_id: int, user_id: int) -> WorkoutPlan | None:
        return self.db.scalar(
            self._base_query().where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user_id)
        )

    def list(
        self,
        *,
        user_id: int,
        search: str | None = None,
        category: str | None = None,
        sort: str = "recent",
    ) -> list[WorkoutPlan]:
        query = self._base_query().where(WorkoutPlan.user_id == user_id)
        if search:
            query = query.where(WorkoutPlan.name.ilike(f"%{search}%"))
        if category and category.lower() != "all":
            query = query.where(WorkoutPlan.category == category.lower())
        if sort == "name":
            query = query.order_by(WorkoutPlan.name)
        else:
            query = query.order_by(WorkoutPlan.created_at.desc())
        return list(self.db.scalars(query))

    def create(
        self,
        *,
        user_id: int,
        name: str,
        description: str | None,
        category: str,
        schedule: dict,
        exercises: list[PlanExerciseIn],
    ) -> WorkoutPlan:
        plan = WorkoutPlan(
            user_id=user_id,
            name=name,
            description=description,
            category=category.lower(),
            schedule=schedule,
        )
        for item in exercises:
            plan.exercises.append(WorkoutPlanExercise(**item.model_dump()))
        self.db.add(plan)
        self.db.commit()
        return self.get_by_id(plan.id, user_id)  # type: ignore[return-value]

    def update(self, plan: WorkoutPlan, data: dict, exercises: list[PlanExerciseIn] | None) -> WorkoutPlan:
        for key, value in data.items():
            if value is not None:
                setattr(plan, key, value)
        if exercises is not None:
            plan.exercises.clear()
            self.db.flush()
            for item in exercises:
                plan.exercises.append(WorkoutPlanExercise(**item.model_dump()))
        self.db.commit()
        return self.get_by_id(plan.id, plan.user_id)  # type: ignore[return-value]

    def delete(self, plan: WorkoutPlan) -> None:
        self.db.delete(plan)
        self.db.commit()
