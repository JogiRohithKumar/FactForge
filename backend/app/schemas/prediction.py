from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings

settings = get_settings()


class TextRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=settings.max_text_length)

    @field_validator("text")
    @classmethod
    def not_just_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty or whitespace-only")
        return v


class UrlRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)

    @field_validator("url")
    @classmethod
    def must_look_like_url(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("url must start with http:// or https://")
        return v


class PredictionResponse(BaseModel):
    id: str
    is_fake: bool
    confidence: float
    source_type: str
    source_preview: str
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
