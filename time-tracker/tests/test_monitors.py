import pytest
from unittest.mock import Mock, patch
import time
from src.monitors.base_monitor import BaseMonitor
from src.monitors.system_monitor import SystemMonitor
from src.monitors.input_monitor import InputMonitor

class TestBaseMonitor:
    """Test the abstract base monitor class."""
    
    class ConcreteMonitor(BaseMonitor):
        """Concrete implementation for testing."""
        def __init__(self):
            super().__init__()
            self._is_active = True
            self._activity = {'name': 'test'}
        
        def get_current_activity(self):
            return self._activity
            
        def is_active(self):
            return self._is_active
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = self.ConcreteMonitor()
        assert monitor.current_activity is None
        assert isinstance(monitor.last_update, float)
    
    def test_update_method(self):
        """Test the update method."""
        monitor = self.ConcreteMonitor()
        
        # First update
        result = monitor.update()
        assert result == {'name': 'test'}
        assert monitor.current_activity == result
        
        # Update with same activity
        first_update = monitor.last_update
        time.sleep(0.1)
        result = monitor.update()
        assert result == {'name': 'test'}
        assert monitor.last_update == first_update  # Shouldn't update timestamp
        
        # Update with different activity
        monitor._activity = {'name': 'new_test'}
        result = monitor.update()
        assert result == {'name': 'new_test'}
        assert monitor.last_update > first_update  # Should update timestamp

class TestSystemMonitor:
    """Test the system monitor implementation."""
    
    @pytest.fixture
    def mock_workspace(self):
        """Mock NSWorkspace for testing."""
        with patch('src.monitors.system_monitor.NSWorkspace') as workspace_mock:
            workspace_instance = Mock()
            workspace_mock.sharedWorkspace.return_value = workspace_instance
            
            # Configure active application mock
            active_app = {
                'NSApplicationName': 'Test App',
                'NSApplicationProcessIdentifier': 12345,
                'NSApplicationBundleIdentifier': 'com.test.app'
            }
            workspace_instance.activeApplication.return_value = active_app
            
            yield workspace_instance
    
    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil for testing."""
        with patch('src.monitors.system_monitor.psutil') as psutil_mock:
            process_mock = Mock()
            process_mock.name.return_value = 'test_process'
            process_mock.exe.return_value = '/usr/bin/test_process'
            psutil_mock.Process.return_value = process_mock
            yield psutil_mock
    
    def test_get_current_activity(self, mock_workspace, mock_psutil):
        """Test getting current system activity."""
        monitor = SystemMonitor()
        activity = monitor.get_current_activity()
        
        assert activity is not None
        assert activity['process_name'] == 'test_process'
        assert activity['window_title'] == 'Test App'
        assert activity['pid'] == 12345
        assert activity['bundle_id'] == 'com.test.app'
    
    def test_handle_no_active_window(self, mock_workspace):
        """Test handling when no window is active."""
        mock_workspace.activeApplication.return_value = None
        monitor = SystemMonitor()
        activity = monitor.get_current_activity()
        
        assert activity is None
    
    def test_handle_process_error(self, mock_workspace, mock_psutil):
        """Test handling process access errors."""
        mock_psutil.Process.side_effect = Exception("Process error")
        monitor = SystemMonitor()
        activity = monitor.get_current_activity()
        
        assert activity is None

class TestInputMonitor:
    """Test the input monitor implementation."""
    
    @pytest.fixture
    def mock_quartz(self):
        """Mock Quartz framework for testing."""
        with patch('src.monitors.input_monitor.Quartz') as quartz_mock:
            # Configure event source mock
            quartz_mock.CGEventSourceSecondsSinceLastEventType.return_value = 1.0
            yield quartz_mock
    
    def test_initialization(self):
        """Test input monitor initialization."""
        monitor = InputMonitor(input_threshold=2.0)
        assert monitor.input_threshold == 2.0
        assert isinstance(monitor.last_input_time, float)
    
    def test_get_last_input_time(self, mock_quartz):
        """Test getting last input time."""
        monitor = InputMonitor()
        last_time = monitor._get_last_input_time()
        
        assert isinstance(last_time, float)
        mock_quartz.CGEventSourceSecondsSinceLastEventType.assert_called_once()
    
    def test_is_active(self, mock_quartz):
        """Test activity detection."""
        monitor = InputMonitor(input_threshold=2.0)
        
        # Test active state
        mock_quartz.CGEventSourceSecondsSinceLastEventType.return_value = 1.0
        assert monitor.is_active() is True
        
        # Test inactive state
        mock_quartz.CGEventSourceSecondsSinceLastEventType.return_value = 3.0
        assert monitor.is_active() is False
    
    def test_get_current_activity(self, mock_quartz):
        """Test getting current input activity state."""
        monitor = InputMonitor()
        activity = monitor.get_current_activity()
        
        assert isinstance(activity, dict)
        assert 'last_input_time' in activity
        assert 'is_active' in activity
        assert 'idle_duration' in activity
    
    def test_handle_no_input_data(self, mock_quartz):
        """Test handling when no input data is available."""
        mock_quartz.CGEventSourceSecondsSinceLastEventType.return_value = None
        monitor = InputMonitor()
        
        # Should fall back to last known input time
        last_time = monitor.last_input_time
        current_time = monitor._get_last_input_time()
        assert current_time == last_time
