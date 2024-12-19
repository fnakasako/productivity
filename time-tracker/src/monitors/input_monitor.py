import time
from typing import Optional, Dict, Any
from .base_monitor import BaseMonitor
import Quartz

class InputMonitor(BaseMonitor):
    """Monitors keyboard and mouse input on macOS."""
    
    def __init__(self, input_threshold: float = 2.0):
        super().__init__()
        self.input_threshold = input_threshold
        self.last_input_time = time.time()
        
    def _get_last_input_time(self) -> float:
        """Get the timestamp of the last input event."""
        # Get the current time in seconds since system startup
        current_time = Quartz.CGEventSourceSecondsSinceLastEventType(
            Quartz.kCGEventSourceStateHIDSystemState,
            Quartz.kCGAnyInputEventType
        )
        
        if current_time is None:
            return self.last_input_time
            
        # Convert to Unix timestamp
        self.last_input_time = time.time() - current_time
        return self.last_input_time
    
    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        """Get current input state."""
        last_input = self._get_last_input_time()
        is_active = self.is_active()
        
        return {
            'last_input_time': last_input,
            'is_active': is_active,
            'idle_duration': time.time() - last_input if not is_active else 0
        }
    
    def is_active(self) -> bool:
        """Check if there's been recent input."""
        last_input = self._get_last_input_time()
        return (time.time() - last_input) < self.input_threshold
