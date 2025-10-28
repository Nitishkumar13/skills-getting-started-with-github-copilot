from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_read_activities():
    """Test that we can get the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Test structure of an activity
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity

def test_signup_for_activity():
    """Test the signup process for an activity"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = next(iter(activities.keys()))
    
    # Test successful signup
    test_email = "test_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
    
    # Test duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    """Test the unregister process for an activity"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = next(iter(activities.keys()))
    
    # First sign up a test student
    test_email = "test_unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Test successful unregister
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {test_email} from {activity_name}"
    
    # Test unregister when not registered
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_invalid_activity():
    """Test handling of invalid activity names"""
    test_email = "test_student@mergington.edu"
    invalid_activity = "NonexistentActivity"
    
    # Test signup for invalid activity
    response = client.post(f"/activities/{invalid_activity}/signup?email={test_email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    
    # Test unregister from invalid activity
    response = client.post(f"/activities/{invalid_activity}/unregister?email={test_email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"