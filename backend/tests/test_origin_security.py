from fastapi.testclient import TestClient
from app.main import app

def test_rejects_untrusted_browser_origin():
    with TestClient(app) as client:
        response = client.post("/auth/logout", headers={"Origin": "https://attacker.example"})
        assert response.status_code == 403

def test_accepts_configured_frontend_origin():
    with TestClient(app) as client:
        response = client.post("/auth/logout", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
