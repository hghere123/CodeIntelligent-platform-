"""Application configuration."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "Code Intelligence Platform"
    api_prefix: str = "/api"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    max_zip_size_mb: int = 500
    database_path: Path = Path("analysis.db")
    worker_count: int = 4

    model_config = SettingsConfigDict(env_prefix="CIP_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

