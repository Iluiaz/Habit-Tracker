"""API tests for Habit Tracker project."""
import pytest

from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as testing_client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield testing_client
        with app.app_context():
            db.session.remove()
            db.drop_all()


class TestHabitAPI:
    def test_create_habit(self, client):
        resp = client.post("/api/habits", json={"title": "Read 20 min"})
        assert resp.status_code == 201
        assert resp.json["title"] == "Read 20 min"
        assert resp.json["streak"] == 0

    def test_create_habit_no_title(self, client):
        resp = client.post("/api/habits", json={})
        assert resp.status_code == 400

    def test_get_habits_empty(self, client):
        resp = client.get("/api/habits")
        assert resp.status_code == 200
        assert resp.json == []

    def test_get_habits_with_data(self, client):
        client.post("/api/habits", json={"title": "Stretch"})
        client.post("/api/habits", json={"title": "Walk"})
        resp = client.get("/api/habits")
        assert resp.status_code == 200
        assert len(resp.json) == 2

    def test_update_habit(self, client):
        created = client.post("/api/habits", json={"title": "Old"})
        hid = created.json["id"]
        resp = client.put(f"/api/habits/{hid}", json={"title": "New"})
        assert resp.status_code == 200
        assert resp.json["title"] == "New"

    def test_update_habit_invalid_frequency(self, client):
        created = client.post("/api/habits", json={"title": "Meditate"})
        hid = created.json["id"]
        resp = client.put(f"/api/habits/{hid}", json={"frequency": "monthly"})
        assert resp.status_code == 400

    def test_delete_habit(self, client):
        created = client.post("/api/habits", json={"title": "Delete"})
        hid = created.json["id"]
        resp = client.delete(f"/api/habits/{hid}")
        assert resp.status_code == 200

        all_resp = client.get("/api/habits")
        assert len(all_resp.json) == 0

    def test_toggle_habit(self, client):
        created = client.post("/api/habits", json={"title": "Toggle"})
        hid = created.json["id"]

        resp1 = client.patch(f"/api/habits/{hid}/toggle")
        assert resp1.status_code == 200
        assert resp1.json["completed_today"] is True
        assert resp1.json["streak"] == 1

        resp2 = client.patch(f"/api/habits/{hid}/toggle")
        assert resp2.status_code == 200
        assert resp2.json["completed_today"] is False

    def test_get_stats(self, client):
        client.post("/api/habits", json={"title": "A"})
        created = client.post("/api/habits", json={"title": "B"})
        hid = created.json["id"]
        client.patch(f"/api/habits/{hid}/toggle")

        resp = client.get("/api/stats")
        assert resp.status_code == 200
        assert resp.json["total_habits"] == 2
        assert resp.json["done_today"] == 1

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/habits/999")
        assert resp.status_code == 404
