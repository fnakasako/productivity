import pytest
from datetime import datetime, timedelta
from pathlib import Path
from src.core.activity import Activity
from src.core.storage import JSONStorage, SQLiteStorage

@pytest.fixture
def json_storage(temp_dir):
    """Create a JSON storage instance for testing."""
    return JSONStorage(temp_dir / "test_activities.json")

@pytest.fixture
def sqlite_storage(temp_dir):
    """Create a SQLite storage instance for testing."""
    return SQLiteStorage(temp_dir / "test_activities.db")

@pytest.fixture
def test_activities():
    """Create a list of test activities."""
    now = datetime.now()
    return [
        Activity(
            name="Activity 1",
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            process_name="process1",
            window_title="Window 1",
            category="Work"
        ),
        Activity(
            name="Activity 2",
            start_time=now - timedelta(minutes=30),
            end_time=now,
            process_name="process2",
            window_title="Window 2",
            category="Personal"
        )
    ]

class TestJSONStorage:
    """Test JSON storage implementation."""
    
    def test_save_and_retrieve(self, json_storage, test_activities):
        """Test saving and retrieving activities."""
        # Save activities
        for activity in test_activities:
            json_storage.save_activity(activity)
        
        # Retrieve all activities
        retrieved = json_storage.get_activities()
        
        assert len(retrieved) == len(test_activities)
        for original, saved in zip(test_activities, retrieved):
            assert saved.name == original.name
            assert saved.process_name == original.process_name
            assert saved.category == original.category
    
    def test_time_filtering(self, json_storage, test_activities):
        """Test filtering activities by time range."""
        # Save activities
        for activity in test_activities:
            json_storage.save_activity(activity)
        
        # Test filtering
        now = datetime.now()
        recent = json_storage.get_activities(
            start_time=now - timedelta(minutes=45)
        )
        assert len(recent) == 1
        assert recent[0].name == "Activity 2"
    
    def test_cleanup(self, json_storage, test_activities):
        """Test cleaning up old activities."""
        # Save activities
        for activity in test_activities:
            json_storage.save_activity(activity)
        
        # Clean up activities older than 1 hour
        json_storage.cleanup_old_activities(days=0.05)  # ~1 hour
        
        # Should only have the recent activity
        remaining = json_storage.get_activities()
        assert len(remaining) == 1
        assert remaining[0].name == "Activity 2"

class TestSQLiteStorage:
    """Test SQLite storage implementation."""
    
    def test_save_and_retrieve(self, sqlite_storage, test_activities):
        """Test saving and retrieving activities."""
        # Save activities
        for activity in test_activities:
            sqlite_storage.save_activity(activity)
        
        # Retrieve all activities
        retrieved = sqlite_storage.get_activities()
        
        assert len(retrieved) == len(test_activities)
        for original, saved in zip(test_activities, retrieved):
            assert saved.name == original.name
            assert saved.process_name == original.process_name
            assert saved.category == original.category
    
    def test_time_filtering(self, sqlite_storage, test_activities):
        """Test filtering activities by time range."""
        # Save activities
        for activity in test_activities:
            sqlite_storage.save_activity(activity)
        
        # Test filtering
        now = datetime.now()
        recent = sqlite_storage.get_activities(
            start_time=now - timedelta(minutes=45)
        )
        assert len(recent) == 1
        assert recent[0].name == "Activity 2"
    
    def test_cleanup(self, sqlite_storage, test_activities):
        """Test cleaning up old activities."""
        # Save activities
        for activity in test_activities:
            sqlite_storage.save_activity(activity)
        
        # Clean up activities older than 1 hour
        sqlite_storage.cleanup_old_activities(days=0.05)  # ~1 hour
        
        # Should only have the recent activity
        remaining = sqlite_storage.get_activities()
        assert len(remaining) == 1
        assert remaining[0].name == "Activity 2"
    
    def test_database_creation(self, temp_dir):
        """Test database and table creation."""
        db_path = temp_dir / "new_db.sqlite"
        storage = SQLiteStorage(db_path)
        
        # Verify database file was created
        assert db_path.exists()
        
        # Verify we can save and retrieve data
        now = datetime.now()
        activity = Activity(
            name="Test Activity",
            start_time=now,
            end_time=now + timedelta(minutes=10),
            process_name="test_process"
        )
        
        storage.save_activity(activity)
        retrieved = storage.get_activities()
        
        assert len(retrieved) == 1
        assert retrieved[0].name == activity.name
