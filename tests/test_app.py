import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory state before every test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_response_contains_expected_activity_names(self):
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_each_activity_has_required_fields(self):
        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_successful_signup_returns_200(self):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_student_added_to_participants(self):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        client.post("/activities/Chess%20Club/signup", params={"email": email})

        # Assert
        assert email in activities["Chess Club"]["participants"]

    def test_unknown_activity_returns_404(self):
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.post(
            "/activities/Unknown%20Activity/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_duplicate_signup_returns_400(self):
        # Arrange
        email = "newstudent@mergington.edu"
        client.post("/activities/Chess%20Club/signup", params={"email": email})

        # Act
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_successful_unregister_returns_200(self):
        # Arrange
        email = "michael@mergington.edu"  # pre-seeded participant

        # Act
        response = client.delete(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_student_removed_from_participants(self):
        # Arrange
        email = "michael@mergington.edu"  # pre-seeded participant

        # Act
        client.delete("/activities/Chess%20Club/signup", params={"email": email})

        # Assert
        assert email not in activities["Chess Club"]["participants"]

    def test_unknown_activity_returns_404(self):
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Unknown%20Activity/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_non_participant_returns_404(self):
        # Arrange
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
