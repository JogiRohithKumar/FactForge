import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    APP_NAME: str = "FactForge"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Security Infrastructure
    API_BEARER_TOKEN: str = os.getenv("API_BEARER_TOKEN", "factforge_dev_secret_token_2026")
    
    # Infrastructure Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # System Operational Parameters
    PROXY_ROTATION_LIST: list[str] = [
        "http://proxy1.example.com:8000",
        "http://proxy2.example.com:8000",
        "http://proxy3.example.com:8000"
    ]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = AppSettings()