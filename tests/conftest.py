import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets activities data to a known state before each test.
    This ensures test isolation by creating a fresh copy of activities.
    """
    from app import activities
    
    # Store original state
    original_state = {}
    for activity_name, activity_data in activities.items():
        original_state[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
    
    yield
    
    # Restore original state after test
    for activity_name in list(activities.keys()):
        if activity_name in original_state:
            activities[activity_name] = original_state[activity_name]
