from sqlalchemy.orm import Session

from app.core.responses import ApiError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def register(self, data: RegisterRequest) -> tuple[User, TokenPair]:
        if self.users.get_by_email(data.email) is not None:
            raise ApiError(400, "An account with this email already exists")
        user = self.users.create(
            email=data.email, name=data.name, hashed_password=hash_password(data.password)
        )
        return user, self._issue_tokens(user)

    def login(self, data: LoginRequest) -> tuple[User, TokenPair]:
        user = self.users.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise ApiError(401, "Invalid email or password")
        return user, self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenPair:
        user_id = decode_token(refresh_token, "refresh")
        if user_id is None:
            raise ApiError(401, "Invalid or expired refresh token")
        user = self.users.get_by_id(int(user_id))
        if user is None:
            raise ApiError(401, "User not found")
        return self._issue_tokens(user)

    @staticmethod
    def _issue_tokens(user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
