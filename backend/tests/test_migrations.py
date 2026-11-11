import os
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from app.core.config import get_settings

def test_migration_upgrades_existing_legacy_history_table(tmp_path, monkeypatch):
    database = tmp_path / "legacy.db"
    engine = create_engine(f"sqlite:///{database}")
    with engine.begin() as connection:
        connection.exec_driver_sql("""
            CREATE TABLE verifications (
                id VARCHAR(36) PRIMARY KEY,
                source_type VARCHAR(10) NOT NULL,
                source_preview VARCHAR(160) NOT NULL,
                is_fake BOOLEAN NOT NULL,
                confidence FLOAT NOT NULL,
                error TEXT,
                created_at DATETIME NOT NULL
            )
        """)
    engine.dispose()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    get_settings.cache_clear()
    try:
        config = Config("alembic.ini")
        command.upgrade(config, "head")
        upgraded = create_engine(f"sqlite:///{database}")
        inspector = inspect(upgraded)
        assert "users" in inspector.get_table_names()
        assert "user_id" in {column["name"] for column in inspector.get_columns("verifications")}
        assert "ix_verifications_user_created" in {index["name"] for index in inspector.get_indexes("verifications")}
        upgraded.dispose()
    finally:
        monkeypatch.delenv("DATABASE_URL", raising=False)
        get_settings.cache_clear()
