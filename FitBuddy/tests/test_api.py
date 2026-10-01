import os
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"
os.environ["GOOGLE_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_profile_and_plan():
    response = client.post("/api/profile", json={
        "name": "Test User",
        "age": 20,
        "goal": "General fitness",
        "fitness_level": "Beginner",
        "days_per_week": 3,
        "equipment": "None"
    })
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.post("/api/plan", json={"user_id": user_id})
    assert response.status_code == 200
    assert "workouts" in response.json()["plan"]


def test_submit_feedback():
    profile = client.post("/api/profile", json={
        "name": "Feedback User",
        "age": 20,
        "goal": "General fitness",
        "fitness_level": "Beginner",
        "days_per_week": 3,
        "equipment": "None"
    })
    assert profile.status_code == 200
    user_id = profile.json()["id"]

    response = client.post("/api/feedback", json={
        "user_id": user_id,
        "message": "The dashboard is easy to use."
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Feedback saved"
