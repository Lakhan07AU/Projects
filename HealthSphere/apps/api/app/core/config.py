"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core
    environment: str = "development"
    secret_key: str = "change-me-in-production"
    jwt_secret: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # Database
    database_url: str = "sqlite:///./data/healthsphere.db"

    # Queue
    redis_url: str = "redis://localhost:6379/0"
    task_queue_mode: str = "inline"  # inline | celery

    # Storage
    storage_provider: str = "local"  # local | s3
    storage_endpoint: Optional[str] = None
    storage_access_key: Optional[str] = None
    storage_secret_key: Optional[str] = None
    storage_bucket: str = "healthsphere-documents"
    local_storage_path: str = "./data/storage"
    max_upload_size_mb: int = 25

    # AI
    ai_provider: str = "mock"  # mock | openai | openai_compatible
    ai_api_key: Optional[str] = None
    ai_base_url: Optional[str] = None
    ai_model: str = "gpt-4o-mini"

    # Maps
    map_provider: str = "mock"  # mock | google
    map_api_key: Optional[str] = None

    # Email
    email_provider: str = "mock"  # mock | smtp
    email_api_key: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "no-reply@healthsphere.local"

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
