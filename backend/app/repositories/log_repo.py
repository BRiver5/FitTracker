from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CalorieLog, WeightLog


class WeightLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, log_id: int, user_id: int) -> WeightLog | None:
        return self.db.scalar(
            select(WeightLog).where(WeightLog.id == log_id, WeightLog.user_id == user_id)
        )

    def list(
        self,
        *,
        user_id: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
    ) -> list[WeightLog]:
        query = select(WeightLog).where(WeightLog.user_id == user_id)
        if date_from is not None:
            query = query.where(WeightLog.logged_at >= date_from)
        if date_to is not None:
            query = query.where(WeightLog.logged_at <= date_to)
        return list(self.db.scalars(query.order_by(WeightLog.logged_at.desc()).limit(limit)))

    def create(self, *, user_id: int, weight_kg: float, logged_at: datetime | None) -> WeightLog:
        log = WeightLog(user_id=user_id, weight_kg=weight_kg)
        if logged_at is not None:
            log.logged_at = logged_at
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def delete(self, log: WeightLog) -> None:
        self.db.delete(log)
        self.db.commit()


class CalorieLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, log_id: int, user_id: int) -> CalorieLog | None:
        return self.db.scalar(
            select(CalorieLog).where(CalorieLog.id == log_id, CalorieLog.user_id == user_id)
        )

    def list(
        self,
        *,
        user_id: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[CalorieLog]:
        query = select(CalorieLog).where(CalorieLog.user_id == user_id)
        if date_from is not None:
            query = query.where(CalorieLog.logged_at >= date_from)
        if date_to is not None:
            query = query.where(CalorieLog.logged_at <= date_to)
        return list(self.db.scalars(query.order_by(CalorieLog.logged_at.desc())))

    def create(self, *, user_id: int, logged_at: datetime | None, **fields) -> CalorieLog:
        log = CalorieLog(user_id=user_id, **fields)
        if logged_at is not None:
            log.logged_at = logged_at
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def delete(self, log: CalorieLog) -> None:
        self.db.delete(log)
        self.db.commit()
