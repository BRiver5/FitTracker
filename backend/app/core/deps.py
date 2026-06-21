from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

# Single-user local app: no authentication. Every request operates as this user.
DEFAULT_USER_ID = 1
DEFAULT_USER_EMAIL = "local@fittracker.app"
DEFAULT_USER_NAME = "Athlete"


def get_or_create_default_user(db: Session) -> User:
    user = db.get(User, DEFAULT_USER_ID)
    if user is None:
        user = User(
            id=DEFAULT_USER_ID,
            email=DEFAULT_USER_EMAIL,
            name=DEFAULT_USER_NAME,
            hashed_password="",
            settings={},
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(db: Session = Depends(get_db)) -> User:
    return get_or_create_default_user(db)
