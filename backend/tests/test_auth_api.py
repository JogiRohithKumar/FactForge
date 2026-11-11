from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.api.routes import auth as auth_routes
from app.db.database import Base, get_db
from app.db.models import Verification
from app.main import app

def test_accounts_cannot_read_each_others_history(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(auth_routes, "enforce_rate_limit", lambda *args, **kwargs: None)
    try:
        with TestClient(app) as client:
            first = client.post("/auth/register", json={"email": "first@example.com", "password": "a-strong-password-123"})
            assert first.status_code == 201
            first_user_id = first.json()["user"]["id"]

            with TestSession() as db:
                db.add(Verification(user_id=first_user_id, source_type="text", source_preview="private first account report", is_fake=False, confidence=50.0))
                db.commit()

            assert len(client.get("/history").json()["items"]) == 1
            client.post("/auth/logout")

            second = client.post("/auth/register", json={"email": "second@example.com", "password": "another-strong-password-456"})
            assert second.status_code == 201
            assert client.get("/history").json()["items"] == []
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
