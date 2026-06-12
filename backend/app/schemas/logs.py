from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WeightLogCreate(BaseModel):
    weight_kg: float = Field(gt=0, lt=500)
    logged_at: datetime | None = None


class WeightLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weight_kg: float
    logged_at: datetime


MealType = Literal["breakfast", "lunch", "dinner", "snacks"]


class CalorieLogCreate(BaseModel):
    meal_type: MealType
    food_name: str = Field(min_length=1, max_length=200)
    kcal: float = Field(ge=0, le=10000)
    protein: float = Field(default=0, ge=0)
    carbs: float = Field(default=0, ge=0)
    fat: float = Field(default=0, ge=0)
    logged_at: datetime | None = None


class CalorieLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meal_type: str
    food_name: str
    kcal: float
    protein: float
    carbs: float
    fat: float
    logged_at: datetime
