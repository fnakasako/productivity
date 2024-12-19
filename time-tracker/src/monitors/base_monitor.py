from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

class BaseMonitor(ABC):
    """Abstract base class for activity monitors."""
    
    def __init__(self):
        self.last_update: datetime = datetime.now()
        self.current_activity: Optional[Dict[str, Any]] = None
    
    @abstractmethod
    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        """Get information about current activity."""
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Check if there's active user interaction."""
        pass
    
    def update(self) -> Optional[Dict[str, Any]]:
        """Update current activity state."""
        current_time = datetime.now()
        activity = self.get_current_activity()
        
        if activity != self.current_activity:
            self.last_update = current_time
            self.current_activity = activity
        
        return activity
