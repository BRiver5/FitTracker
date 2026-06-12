from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import envelope
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest
from app.schemas.user import UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user, tokens = AuthService(db).register(data)
    return envelope(
        {"user": UserOut.model_validate(user), "tokens": tokens},
        "Account created",
        201,
    )


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user, tokens = AuthService(db).login(data)
    return envelope({"user": UserOut.model_validate(user), "tokens": tokens}, "Logged in")


@router.post("/refresh")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    tokens = AuthService(db).refresh(data.refresh_token)
    return envelope(tokens, "Token refreshed")


@router.post("/logout")
def logout():
    # Stateless JWT: client discards tokens. Endpoint exists for API symmetry.
    return envelope(None, "Logged out")
