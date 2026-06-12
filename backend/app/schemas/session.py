from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.workout import ExerciseOut


class SessionCreate(BaseModel):
    plan_id: int | None = None


class SessionUpdate(BaseModel):
    finished: bool | None = None
    notes: str | None = None


class SessionSetCreate(BaseModel):
    exercise_id: int
    set_number: int = Field(ge=1, le=100)
    reps: int | None = Field(default=None, ge=0, le=500)
    weight_kg: float | None = Field(default=None, ge=0, le=1000)


class SessionSetUpdate(BaseModel):
    reps: int | None = Field(default=None, ge=0, le=500)
    weight_kg: float | None = Field(default=None, ge=0, le=1000)


class SessionSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    set_number: int
    reps: int | None = None
    weight_kg: float | None = None
    completed_at: datetime
    exercise: ExerciseOut


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int | None = None
    started_at: datetime
    finished_at: datetime | None = None
    notes: str | None = None
    sets: list[SessionSetOut]
