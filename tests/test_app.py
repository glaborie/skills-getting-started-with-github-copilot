import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture()
def client():
    snapshot = copy.deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(snapshot)


def test_get_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Tennis Club" in data
    assert "participants" in data["Tennis Club"]


def test_signup_and_unregister_participant(client):
    activity_name = "Tennis Club"
    email = "testuser@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    delete_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert delete_response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    activity_name = "Tennis Club"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404


def test_duplicate_signup_returns_400(client):
    activity_name = "Tennis Club"
    email = activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400


def test_activity_not_found_returns_404(client):
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 404
