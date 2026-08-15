"""Application configuration.

All secrets and environment-specific values are read from environment
variables (or a local ``.env`` file). Never hard-code credentials.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    APP_NAME: str = "RoadGuard AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- Database ---
    # Default is SQLite so the project runs without any external service.
    # Point DATABASE_URL at a PostgreSQL + PostGIS instance for production.
    DATABASE_URL: str = "sqlite:///./roadguard.db"

    # --- Security ---
    JWT_SECRET: str = "change-me-in-production-roadguard"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12

    # --- Demo / AI ---
    DEMO_MODE: bool = True
    MODEL_PATH: str = ""
    DEMO_BANNER: str = "Demo Mode: AI results are simulated for demonstration."

    # --- Files ---
    STORAGE_PATH: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_MB: float = 15.0
    ALLOWED_IMAGE_EXT: str = ".jpg,.jpeg,.png,.webp"

    # --- CORS ---
    CORS_ORIGINS: str = "*"

    # --- LLM (OpenAI compatible) ---
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_ENABLED: bool = False

    # --- Seed ---
    SEED_ORGANIZATION: str = "Municipal Corporation"

    @property
    def storage_path(self) -> Path:
        return Path(self.STORAGE_PATH)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_extensions(self) -> set[str]:
        return {e.strip().lower() for e in self.ALLOWED_IMAGE_EXT.split(",") if e.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
