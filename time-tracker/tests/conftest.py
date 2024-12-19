import pytest
import tempfile
import yaml
from pathlib import Path
from datetime import datetime

@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def test_config(temp_dir):
    """Provide a test configuration."""
    config = {
        'app': {
            'name': 'TimeTracker',
            'version': '1.0.0'
        },
        'monitoring': {
            'inactivity_threshold': 300,
            'polling_interval': 1.0,
            'input_threshold': 2.0
        },
        'storage': {
            'type': 'json',
            'path': str(temp_dir),
            'filename': 'test_activities.json'
        },
        'ui': {
            'window_title': 'TimeTracker (Test)',
            'window_size': '500x400',
            'theme': 'system',
            'recent_activities_count': 10
        },
        'reporting': {
            'daily_report_time': '23:59',
            'report_format': 'text',
            'group_by_application': True
        }
    }
    return config

@pytest.fixture
def sample_activity():
    """Provide a sample activity for testing."""
    return {
        'name': 'Test Activity',
        'start_time': datetime.now(),
        'process_name': 'test_process',
        'window_title': 'Test Window',
        'category': 'Testing'
    }

@pytest.fixture
def config_file(test_config, temp_dir):
    """Create a temporary config file."""
    config_path = temp_dir / 'test_config.yaml'
    with config_path.open('w') as f:
        yaml.dump(test_config, f)
    return config_path

@pytest.fixture
def mock_system_info():
    """Provide mock system activity info."""
    return {
        'process_name': 'test_app',
        'window_title': 'Test Window',
        'executable': '/usr/bin/test_app',
        'pid': 12345,
        'bundle_id': 'com.test.app'
    }

@pytest.fixture
def mock_input_info():
    """Provide mock input activity info."""
    return {
        'last_input_time': datetime.now().timestamp(),
        'is_active': True,
        'idle_duration': 0
    }
