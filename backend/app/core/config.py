"""Centralized environment-driven configuration."""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", protected_namespaces=())
    app_name: str = "FactForge API"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = f"sqlite:///{BASE_DIR / 'factforge.db'}"
    model_path: Path = BASE_DIR / "app" / "model" / "fake_news_model.pkl"
    vectorizer_path: Path = BASE_DIR / "app" / "model" / "tfidf_vectorizer.pkl"
    max_text_length: int = 20000
    max_scraped_text_length: int = 30000
    scrape_timeout_seconds: float = 8.0
    google_fact_check_api_key: str | None = None
    tavily_api_key: str | None = None
    huggingface_api_token: str | None = None
    jwt_secret_key: str = "local-development-only-change-this-secret"
    access_token_minutes: int = 60
    cookie_secure: bool | None = None
    redis_url: str = "redis://localhost:6379/0"
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    @property
    def use_secure_cookies(self) -> bool:
        return self.is_production if self.cookie_secure is None else self.cookie_secure

@lru_cache
def get_settings() -> Settings:
    return Settings()
