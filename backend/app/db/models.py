import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Verification(Base):
    """A single fact-check run, persisted so history survives a page refresh."""

    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source_type: Mapped[str] = mapped_column(String(10))  # "text" | "url"
    # Truncated preview only — we deliberately do not store full scraped
    # article bodies long-term to keep storage bounded and avoid
    # inadvertently retaining third-party copyrighted content verbatim.
    source_preview: Mapped[str] = mapped_column(String(160))
    is_fake: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[float] = mapped_column(Float)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
