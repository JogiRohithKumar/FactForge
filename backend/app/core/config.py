"""
Centralized application configuration.

Everything here is overridable via environment variables (or a `.env` file
in local dev), so no secrets or environment-specific values are hardcoded
in the app code. See `.env.example` for the full list.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "FactForge API"
    environment: str = "development"  # development | production
    log_level: str = "INFO"

    # --- CORS ---
    cors_origins: List[str] = ["http://localhost:3000"]

    # --- Database ---
    database_url: str = f"sqlite:///{BASE_DIR / 'factforge.db'}"

    # --- ML model artifacts ---
    model_path: Path = BASE_DIR / "app" / "model" / "fake_news_model.pkl"
    vectorizer_path: Path = BASE_DIR / "app" / "model" / "tfidf_vectorizer.pkl"

    # --- Request limits ---
    max_text_length: int = 20_000  # characters
    scrape_timeout_seconds: float = 8.0

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
