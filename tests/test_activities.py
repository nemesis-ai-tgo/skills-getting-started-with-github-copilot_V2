import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """
        Arrange: Set up the test client
        Act: Make a GET request to /activities
        Assert: Verify the response contains all activities
        """
        # Arrange
        expected_activities_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == expected_activities_count
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Basketball Team" in activities_data
        assert activities_data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert activities_data["Chess Club"]["max_participants"] == 12


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """
        Arrange: Prepare an activity and student email
        Act: Sign up the student for an activity
        Assert: Verify the signup was successful
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify student was added to participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """
        Arrange: Set up an activity with an existing participant
        Act: Try to sign up the same student again
        Assert: Verify the signup fails with appropriate error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_at_capacity(self, client, reset_activities):
        """
        Arrange: Set up an activity with limited capacity
        Act: Sign up students until capacity is reached, then try one more
        Assert: Verify the final signup fails with capacity error
        """
        # Arrange
        from app import activities
        activity_name = "Basketball Team"
        activity = activities[activity_name]
        # Fill up the activity to max capacity
        max_participants = activity["max_participants"]
        for i in range(max_participants):
            activity["participants"].append(f"student{i}@mergington.edu")
        
        email = "over_capacity@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """
        Arrange: Prepare a non-existent activity name
        Act: Try to sign up for the non-existent activity
        Assert: Verify the signup fails with 404 error
        """
        # Arrange
        activity_name = "NonExistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Test suite for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """
        Arrange: Sign up a student for an activity
        Act: Unregister the student from the activity
        Assert: Verify the unregistration was successful
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify student is initially registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify student was removed from participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """
        Arrange: Prepare a student not registered for an activity
        Act: Try to unregister the student from the activity
        Assert: Verify the unregistration fails with appropriate error
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """
        Arrange: Prepare a non-existent activity name
        Act: Try to unregister from the non-existent activity
        Assert: Verify the unregistration fails with 404 error
        """
        # Arrange
        activity_name = "NonExistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
