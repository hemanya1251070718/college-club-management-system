import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_campus_data_endpoint(client):
    """Verifies that /api/campus-data returns all 75 students, 5 clubs, 12 events, 92 memberships."""
    res = client.get("/api/campus-data")
    assert res.status_code == 200
    data = res.get_json()
    assert "students" in data
    assert "clubs" in data
    assert "events" in data
    assert "memberships" in data
    assert "registrations" in data
    assert "reviews" in data
    assert "audit" in data

    assert len(data["students"]) == 75
    assert len(data["clubs"]) == 5
    assert len(data["events"]) == 12
    assert len(data["memberships"]) == 94
    assert len(data["registrations"]) == 30
    assert len(data["reviews"]) == 15
