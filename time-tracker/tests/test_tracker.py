import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import time
from src.core.tracker import ActivityTracker
from src.core.activity import Activity

@pytest.fixture
def mock_monitors():
    """Create mock system and input monitors."""
    with patch('src.core.tracker.SystemMonitor') as system_mock, \
         patch('src.core.tracker.InputMonitor') as input_mock:
        
        # Configure system monitor mock
        system_instance = system_mock.return_value
        system_instance.get_current_activity.return_value = {
            'process_name': 'test_app',
            'window_title': 'Test Window',
            'executable': '/usr/bin/test_app',
            'pid': 12345
        }
        
        # Configure input monitor mock
        input_instance = input_mock.return_value
        input_instance.is_active.return_value = True
        input_instance._get_last_input_time.return_value = time.time()
        
        yield system_instance, input_instance

@pytest.fixture
def tracker(test_config, mock_monitors):
    """Create a tracker instance with mocked monitors."""
    return ActivityTracker(test_config)

class TestActivityTracker:
    """Test the core activity tracking functionality."""
    
    def test_tracker_initialization(self, tracker, test_config):
        """Test tracker initialization."""
        assert tracker.config == test_config
        assert tracker.current_activity is None
        assert tracker.tracking_thread is None
        assert tracker.inactivity_threshold == test_config['monitoring']['inactivity_threshold']
        assert tracker.polling_interval == test_config['monitoring']['polling_interval']
    
    def test_start_stop_tracking(self, tracker):
        """Test starting and stopping activity tracking."""
        # Start tracking
        tracker.start()
        assert tracker.tracking_thread is not None
        assert tracker.tracking_thread.is_alive()
        assert not tracker.stop_event.is_set()
        
        # Stop tracking
        tracker.stop()
        assert not tracker.tracking_thread.is_alive()
        assert tracker.stop_event.is_set()
        assert tracker.current_activity is None
    
    def test_activity_tracking(self, tracker, mock_monitors):
        """Test activity tracking functionality."""
        system_monitor, input_monitor = mock_monitors
        
        # Configure mock to simulate an active window
        system_monitor.get_current_activity.return_value = {
            'process_name': 'test_app',
            'window_title': 'Test Window'
        }
        input_monitor.is_active.return_value = True
        
        # Start tracking and let it run briefly
        tracker.start()
        time.sleep(0.1)  # Allow the tracking loop to run
        
        # Verify current activity
        assert tracker.current_activity is not None
        assert tracker.current_activity.process_name == 'test_app'
        assert tracker.current_activity.window_title == 'Test Window'
        
        # Stop tracking
        tracker.stop()
    
    def test_inactivity_handling(self, tracker, mock_monitors):
        """Test handling of user inactivity."""
        system_monitor, input_monitor = mock_monitors
        
        # Start with active state
        system_monitor.get_current_activity.return_value = {
            'process_name': 'test_app',
            'window_title': 'Test Window'
        }
        input_monitor.is_active.return_value = True
        
        # Start tracking
        tracker.start()
        time.sleep(0.1)  # Allow the tracking loop to run
        
        # Verify activity started
        assert tracker.current_activity is not None
        initial_activity = tracker.current_activity
        
        # Simulate inactivity
        input_monitor.is_active.return_value = False
        input_monitor._get_last_input_time.return_value = (
            time.time() - tracker.inactivity_threshold - 1
        )
        
        time.sleep(tracker.polling_interval * 2)  # Allow the tracking loop to detect inactivity
        
        # Verify activity was ended
        assert tracker.current_activity is None
        assert initial_activity.end_time is not None
        
        # Stop tracking
        tracker.stop()
    
    def test_activity_change(self, tracker, mock_monitors):
        """Test handling of activity changes."""
        system_monitor, input_monitor = mock_monitors
        
        # Start with one activity
        system_monitor.get_current_activity.return_value = {
            'process_name': 'app1',
            'window_title': 'Window 1'
        }
        input_monitor.is_active.return_value = True
        
        # Start tracking
        tracker.start()
        time.sleep(0.1)  # Allow the tracking loop to run
        
        # Verify first activity
        assert tracker.current_activity.process_name == 'app1'
        first_activity = tracker.current_activity
        
        # Change to new activity
        system_monitor.get_current_activity.return_value = {
            'process_name': 'app2',
            'window_title': 'Window 2'
        }
        
        time.sleep(tracker.polling_interval * 2)  # Allow the tracking loop to detect change
        
        # Verify activity changed
        assert tracker.current_activity.process_name == 'app2'
        assert first_activity.end_time is not None
        
        # Stop tracking
        tracker.stop()
    
    def test_get_activities(self, tracker, test_activities):
        """Test retrieving activities."""
        # Save some test activities
        for activity in test_activities:
            tracker.storage.save_activity(activity)
        
        # Test retrieving all activities
        all_activities = tracker.get_activities()
        assert len(all_activities) == len(test_activities)
        
        # Test retrieving activities with time range
        now = datetime.now()
        recent = tracker.get_activities(
            start_time=now - timedelta(minutes=45)
        )
        assert len(recent) == 1
        assert recent[0].name == "Activity 2"
    
    def test_daily_summary(self, tracker, test_activities):
        """Test getting daily activity summary."""
        # Save test activities
        for activity in test_activities:
            tracker.storage.save_activity(activity)
        
        # Get summary for today
        summary = tracker.get_daily_summary()
        
        # Verify summary
        assert len(summary) == 2  # Two different processes
        assert 'process1' in summary
        assert 'process2' in summary
        assert summary['process1'] == 60.0  # 1 hour activity
        assert summary['process2'] == 30.0  # 30 minutes activity
