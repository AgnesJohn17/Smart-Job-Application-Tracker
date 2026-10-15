"""End-to-end API workflow coverage: dates, searches and tenant isolation."""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-only-secret"
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

def account(client):
    email = f"{uuid4().hex}@example.com"
    response = client.post("/api/auth/register", json={"email": email, "password": "AsecurePass123!"})
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_application_with_dates_and_url():
    with TestClient(app) as client:
        auth = account(client)
        create = client.post("/api/applications", headers=auth, json={
            "company": "Example Tech",
            "role": "Full Stack Developer Intern",
            "status": "Applied",
            "applied_date": "2026-10-14",
            "deadline": "2027-01-20",
            "url": "https://example.com/careers",
            "location": "Toronto",
            "notes": "Follow up after applying"
        })
        assert create.status_code == 201, create.text
        record = create.json()
        assert record["applied_date"] == "2026-10-14"
        assert record["deadline"] == "2027-01-20"
        assert record["url"] == "https://example.com/careers"
        update = client.patch(f"/api/applications/{record['id']}", headers=auth,
                              json={"status": "Interview", "deadline": "2027-02-01",
                                    "applied_date": None, "url": None})
        assert update.status_code == 200, update.text
        assert update.json()["deadline"] == "2027-02-01"
        assert update.json()["applied_date"] is None
        assert update.json()["url"] is None
        assert len(client.get("/api/applications", headers=auth,
                              params={"q": "developer", "stage": "Interview"}).json()) == 1

def test_other_user_cannot_read_or_modify_and_invalid_token_rejected():
    with TestClient(app) as client:
        owner = account(client)
        other = account(client)
        entry = client.post("/api/applications", headers=owner,
                            json={"company": "Example Corp", "role": "Developer"}).json()
        assert client.get("/api/applications", headers=other).json() == []
        assert client.get("/api/dashboard", headers=other).json()["total"] == 0
        assert client.patch(f"/api/applications/{entry['id']}", headers=other,
                            json={"status":"Offer"}).status_code == 404
        assert client.delete(f"/api/applications/{entry['id']}", headers=other).status_code == 404
        assert client.get("/api/applications",
                          headers={"Authorization": "Bearer invalid.token"}).status_code == 401
        assert client.get("/api/dashboard", headers=owner).json()["total"] == 1
