import pytest
from fastapi.testclient import TestClient


class TestActivitiesEndpoints:
    """Tests for activities API endpoints"""

    def test_get_root_redirect(self, client):
        """Test that the root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_get_activities(self, client):
        """Test that we can retrieve all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        
        # Verify expected activities exist
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball",
            "Tennis",
            "Debate Club",
            "Science Club",
            "Drama Club",
            "Visual Arts"
        ]
        for activity in expected_activities:
            assert activity in activities
        
        # Verify activity structure
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_activity_has_correct_structure(self, client):
        """Test that each activity has the correct data structure"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for signup functionality"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_appears_in_participants(self, client):
        """Test that a newly signed up participant appears in the participants list"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        response = client.post(f"/activities/Tennis/signup?email={email}")
        assert response.status_code == 200
        
        # Verify they appear in the participants list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Tennis"]["participants"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signups are rejected"""
        email = "michael@mergington.edu"
        
        # Michael is already signed up for Chess Club
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test that signup fails for nonexistent activities"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for unregister functionality"""

    def test_unregister_participant_success(self, client):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"
        
        # Michael is in Chess Club, so unregister should work
        response = client.post(f"/activities/Chess%20Club/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregistered participant is removed from list"""
        email = "daniel@mergington.edu"
        
        # Daniel is in Chess Club
        response = client.get("/activities")
        activities_before = response.json()
        assert email in activities_before["Chess Club"]["participants"]
        
        # Unregister Daniel
        client.post(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify Daniel is no longer in the list
        response = client.get("/activities")
        activities_after = response.json()
        assert email not in activities_after["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self, client):
        """Test that unregistering a non-participant fails"""
        email = "notregistered@mergington.edu"
        
        response = client.post(f"/activities/Chess%20Club/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test that unregister fails for nonexistent activities"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
