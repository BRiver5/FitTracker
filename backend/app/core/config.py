from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "FitTracker API"
    DEBUG: bool = False

    # Local-first: a single SQLite file next to the backend. No external DB/Docker needed.
    DATABASE_URL: str = "sqlite:///./fittracker.db"

    # Comma-separated list of allowed origins. Expo dev tools use various ports.
    CORS_ORIGINS: str = "http://localhost:8081,http://localhost:19006,exp://localhost:8081,https://fittracker.app"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
