import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, AnyHttpUrl, validator


class Settings(BaseSettings):
    app_name: str = "Doodlebucks API"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/doodlebucks"
    jwt_secret: str = "change-me"
    jwt_issuer: str = "doodlebucks-api"
    jwt_audience: str = "doodlebucks-web"
    jwt_exp_minutes: int = 60
    discord_client_id: Optional[str] = None
    discord_client_secret: Optional[str] = None
    oauth_redirect_uri: Optional[AnyHttpUrl] = None
    frontend_origin: Optional[AnyHttpUrl] = None

    class Config:
        env_file = ".env"
        env_prefix = "DOODLE_"

    @validator("jwt_secret")
    def _ensure_secret(cls, v: str) -> str:
        if v == "change-me":
            raise ValueError("Set DOODLE_JWT_SECRET in env for security.")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
