from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import envelope
from app.models import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserOut, UserSettingsUpdate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return envelope(UserOut.model_validate(user))


@router.put("/me")
def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = UserRepository(db).update(user, **data.model_dump(exclude_unset=True))
    return envelope(UserOut.model_validate(updated), "Profile updated")


@router.put("/me/settings")
def update_settings(
    data: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    merged = {**(user.settings or {}), **data.settings}
    updated = UserRepository(db).update(user, settings=merged)
    return envelope(UserOut.model_validate(updated), "Settings updated")
