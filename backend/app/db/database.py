from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# check_same_thread is only needed for SQLite; harmless to set unconditionally
# since we only ever target SQLite or Postgres in this project.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models here (not at module top) so they're registered on Base
    # before create_all runs, without creating a circular import.
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
