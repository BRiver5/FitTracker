from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ApiError, envelope
from app.models import User
from app.repositories.session_repo import SessionRepository
from app.schemas.session import (
    SessionCreate,
    SessionOut,
    SessionSetCreate,
    SessionSetOut,
    SessionSetUpdate,
    SessionUpdate,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("")
def start_session(
    data: SessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SessionRepository(db).create(user_id=user.id, plan_id=data.plan_id)
    return envelope(SessionOut.model_validate(session), "Session started", 201)


@router.get("")
def list_sessions(
    plan_id: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = SessionRepository(db).list(
        user_id=user.id,
        plan_id=plan_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return envelope([SessionOut.model_validate(s) for s in sessions])


@router.get("/{session_id}")
def get_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SessionRepository(db).get_by_id(session_id, user.id)
    if session is None:
        raise ApiError(404, "Session not found")
    return envelope(SessionOut.model_validate(session))


@router.put("/{session_id}")
def update_session(
    session_id: int,
    data: SessionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id, user.id)
    if session is None:
        raise ApiError(404, "Session not found")
    updated = repo.update(session, finished=data.finished, notes=data.notes)
    return envelope(SessionOut.model_validate(updated), "Session updated")


@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id, user.id)
    if session is None:
        raise ApiError(404, "Session not found")
    repo.delete(session)
    return envelope(None, "Session deleted")


@router.post("/{session_id}/sets")
def add_set(
    session_id: int,
    data: SessionSetCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id, user.id)
    if session is None:
        raise ApiError(404, "Session not found")
    session_set = repo.add_set(session, **data.model_dump())
    return envelope(SessionSetOut.model_validate(session_set), "Set logged", 201)


@router.put("/{session_id}/sets/{set_id}")
def update_set(
    session_id: int,
    set_id: int,
    data: SessionSetUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id, user.id)
    if session is None:
        raise ApiError(404, "Session not found")
    session_set = repo.get_set(session_id, set_id)
    if session_set is None:
        raise ApiError(404, "Set not found")
    updated = repo.update_set(session_set, **data.model_dump(exclude_unset=True))
    return envelope(SessionSetOut.model_validate(updated), "Set updated")
