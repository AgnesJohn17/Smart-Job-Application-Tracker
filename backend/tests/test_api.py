import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-only-secret"
from fastapi.testclient import TestClient
from app.main import app

def test_user_isolation_and_crud():
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        a = client.post("/api/auth/register", json={"email":"a@example.com","password":"password123"})
        b = client.post("/api/auth/register", json={"email":"b@example.com","password":"password123"})
        assert a.status_code == b.status_code == 201
        ha = {"Authorization": "Bearer " + a.json()["access_token"]}
        hb = {"Authorization": "Bearer " + b.json()["access_token"]}
        assert client.get("/api/applications").status_code == 403 or client.get("/api/applications").status_code == 401
        created = client.post("/api/applications", headers=ha, json={"company":"OpenAI","role":"Software Intern","status":"Applied"})
        assert created.status_code == 201, created.text
        entry = created.json()["id"]
        assert len(client.get("/api/applications", headers=ha).json()) == 1
        assert client.get("/api/applications", headers=hb).json() == []
        assert client.patch(f"/api/applications/{entry}", headers=hb, json={"status":"Offer"}).status_code == 404
        assert client.delete(f"/api/applications/{entry}", headers=hb).status_code == 404
        changed = client.patch(f"/api/applications/{entry}", headers=ha, json={"status":"Interview"})
        assert changed.json()["status"] == "Interview"
        assert client.get("/api/dashboard", headers=ha).json()["Interview"] == 1
        assert len(client.get("/api/applications", headers=ha, params={"q":"OpenAI","stage":"Interview"}).json()) == 1
        assert client.delete(f"/api/applications/{entry}", headers=ha).status_code == 204
        assert client.get("/api/dashboard", headers=ha).json()["total"] == 0

def test_validation_and_login():
    with TestClient(app) as client:
        bad = client.post("/api/auth/register", json={"email":"bad","password":"short"})
        assert bad.status_code == 422
        client.post("/api/auth/register", json={"email":"login@example.com","password":"password123"})
        assert client.post("/api/auth/login", json={"email":"login@example.com","password":"incorrect"}).status_code == 401
        logged = client.post("/api/auth/login", json={"email":"login@example.com","password":"password123"})
        assert logged.status_code == 200
        h={"Authorization":"Bearer "+logged.json()["access_token"]}
        assert client.post("/api/applications",headers=h,json={"company":" ","role":"Analyst"}).status_code == 422
