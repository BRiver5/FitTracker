from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    muscle_groups: list[str]
    instructions: str | None = None
    is_default: bool


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=40)
    muscle_groups: list[str] = []
    instructions: str | None = None


class PlanExerciseIn(BaseModel):
    exercise_id: int
    sets: int = Field(default=3, ge=1, le=20)
    reps: int | None = Field(default=None, ge=1, le=200)
    duration_seconds: int | None = Field(default=None, ge=1)
    rest_seconds: int = Field(default=60, ge=0, le=600)
    order_index: int = 0


class PlanExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    sets: int
    reps: int | None = None
    duration_seconds: int | None = None
    rest_seconds: int
    order_index: int
    exercise: ExerciseOut


class WorkoutPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    category: str = "custom"
    schedule: dict = {}
    exercises: list[PlanExerciseIn] = []


class WorkoutPlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    category: str | None = None
    schedule: dict | None = None
    exercises: list[PlanExerciseIn] | None = None


class WorkoutPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    category: str
    schedule: dict
    created_at: datetime
    exercises: list[PlanExerciseOut]
