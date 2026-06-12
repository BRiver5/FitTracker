from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import SessionSet, WorkoutSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return select(WorkoutSession).options(
            selectinload(WorkoutSession.sets).selectinload(SessionSet.exercise)
        )

    def get_by_id(self, session_id: int, user_id: int) -> WorkoutSession | None:
        return self.db.scalar(
            self._base_query().where(
                WorkoutSession.id == session_id, WorkoutSession.user_id == user_id
            )
        )

    def list(
        self,
        *,
        user_id: int,
        plan_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkoutSession]:
        query = self._base_query().where(WorkoutSession.user_id == user_id)
        if plan_id is not None:
            query = query.where(WorkoutSession.plan_id == plan_id)
        if date_from is not None:
            query = query.where(WorkoutSession.started_at >= date_from)
        if date_to is not None:
            query = query.where(WorkoutSession.started_at <= date_to)
        query = query.order_by(WorkoutSession.started_at.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(query))

    def create(self, *, user_id: int, plan_id: int | None) -> WorkoutSession:
        session = WorkoutSession(user_id=user_id, plan_id=plan_id)
        self.db.add(session)
        self.db.commit()
        return self.get_by_id(session.id, user_id)  # type: ignore[return-value]

    def update(self, session: WorkoutSession, *, finished: bool | None, notes: str | None) -> WorkoutSession:
        if finished:
            session.finished_at = datetime.now(timezone.utc)
        if notes is not None:
            session.notes = notes
        self.db.commit()
        return self.get_by_id(session.id, session.user_id)  # type: ignore[return-value]

    def delete(self, session: WorkoutSession) -> None:
        self.db.delete(session)
        self.db.commit()

    def add_set(self, session: WorkoutSession, **fields) -> SessionSet:
        session_set = SessionSet(session_id=session.id, **fields)
        self.db.add(session_set)
        self.db.commit()
        self.db.refresh(session_set)
        return session_set

    def get_set(self, session_id: int, set_id: int) -> SessionSet | None:
        return self.db.scalar(
            select(SessionSet).where(SessionSet.id == set_id, SessionSet.session_id == session_id)
        )

    def update_set(self, session_set: SessionSet, **fields) -> SessionSet:
        for key, value in fields.items():
            if value is not None:
                setattr(session_set, key, value)
        self.db.commit()
        self.db.refresh(session_set)
        return session_set
