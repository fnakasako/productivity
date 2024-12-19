import pytest
from datetime import datetime, timedelta
from src.core.activity import Activity

def test_activity_creation():
    """Test basic activity creation."""
    now = datetime.now()
    activity = Activity(
        name="Test Activity",
        start_time=now,
        process_name="test_process",
        window_title="Test Window"
    )
    
    assert activity.name == "Test Activity"
    assert activity.start_time == now
    assert activity.process_name == "test_process"
    assert activity.window_title == "Test Window"
    assert activity.end_time is None
    assert activity.category is None

def test_activity_duration():
    """Test activity duration calculation."""
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)
    
    activity = Activity(
        name="Test Activity",
        start_time=start_time,
        end_time=end_time
    )
    
    assert activity.duration_minutes == 30.0

def test_activity_serialization():
    """Test activity serialization to/from dict."""
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=45)
    
    original = Activity(
        name="Test Activity",
        start_time=start_time,
        end_time=end_time,
        process_name="test_process",
        window_title="Test Window",
        category="Testing"
    )
    
    # Convert to dict
    activity_dict = original.to_dict()
    
    # Create new activity from dict
    restored = Activity.from_dict(activity_dict)
    
    # Verify all attributes match
    assert restored.name == original.name
    assert restored.start_time == original.start_time
    assert restored.end_time == original.end_time
    assert restored.process_name == original.process_name
    assert restored.window_title == original.window_title
    assert restored.category == original.category
    assert restored.duration_minutes == original.duration_minutes

def test_activity_no_end_time():
    """Test activity with no end time."""
    start_time = datetime.now()
    
    activity = Activity(
        name="Test Activity",
        start_time=start_time
    )
    
    assert activity.duration_minutes == 0.0
    
    # Test serialization with no end time
    activity_dict = activity.to_dict()
    restored = Activity.from_dict(activity_dict)
    
    assert restored.end_time is None
    assert restored.duration_minutes == 0.0
