from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Save and restore in-memory activities state between tests."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities():
    # Arrange
    expected = "Chess Club"

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert expected in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "test_signup@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity]["participants"].count(email) == 1


def test_unregister_from_activity_removes_participant():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    resp = client.delete(f"/activities/{quote(activity)}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "not_a_student@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    resp = client.delete(f"/activities/{quote(activity)}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is not signed up for this activity"
