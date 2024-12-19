import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from threading import Thread, Event
from .activity import Activity
from .storage import BaseStorage, JSONStorage, SQLiteStorage
from ..monitors.system_monitor import SystemMonitor
from ..monitors.input_monitor import InputMonitor

logger = logging.getLogger(__name__)

class ActivityTracker:
    """Core class for tracking user activities."""
    
    def __init__(self, config: dict):
        self.config = config
        self.storage = self._init_storage()
        self.system_monitor = SystemMonitor()
        self.input_monitor = InputMonitor(
            input_threshold=config['monitoring']['input_threshold']
        )
        
        self.current_activity: Optional[Activity] = None
        self.stop_event = Event()
        self.tracking_thread: Optional[Thread] = None
        
        # Configuration
        self.inactivity_threshold = config['monitoring']['inactivity_threshold']
        self.polling_interval = config['monitoring']['polling_interval']
    
    def _init_storage(self) -> BaseStorage:
        """Initialize storage backend based on configuration."""
        storage_config = self.config['storage']
        storage_path = Path(storage_config['path']).expanduser()
        
        if storage_config['type'] == 'sqlite':
            return SQLiteStorage(storage_path / 'activities.db')
        else:  # default to JSON
            return JSONStorage(storage_path / storage_config['filename'])
    
    def start(self) -> None:
        """Start activity tracking in a background thread."""
        if self.tracking_thread and self.tracking_thread.is_alive():
            logger.warning("Tracking already running")
            return
            
        self.stop_event.clear()
        self.tracking_thread = Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        logger.info("Activity tracking started")
    
    def stop(self) -> None:
        """Stop activity tracking."""
        if not self.tracking_thread:
            return
            
        self.stop_event.set()
        self.tracking_thread.join()
        self._end_current_activity()
        logger.info("Activity tracking stopped")
    
    def _tracking_loop(self) -> None:
        """Main tracking loop."""
        while not self.stop_event.is_set():
            try:
                self._update_activity()
                time.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}", exc_info=True)
    
    def _update_activity(self) -> None:
        """Update current activity based on system and input state."""
        system_info = self.system_monitor.get_current_activity()
        is_active = self.input_monitor.is_active()
        
        if not system_info or not is_active:
            self._handle_inactivity()
            return
            
        # Check if this is a new activity
        if (not self.current_activity or
            self.current_activity.process_name != system_info['process_name'] or
            self.current_activity.window_title != system_info['window_title']):
            self._start_new_activity(system_info)
    
    def _start_new_activity(self, system_info: Dict[str, Any]) -> None:
        """Start tracking a new activity."""
        if self.current_activity:
            self._end_current_activity()
            
        self.current_activity = Activity(
            name=system_info['window_title'],
            start_time=datetime.now(),
            process_name=system_info['process_name'],
            window_title=system_info['window_title']
        )
        logger.debug(f"Started new activity: {self.current_activity.name}")
    
    def _end_current_activity(self) -> None:
        """End the current activity and save it."""
        if not self.current_activity:
            return
            
        self.current_activity.end_time = datetime.now()
        if self.current_activity.duration_minutes > 0:
            self.storage.save_activity(self.current_activity)
            logger.debug(
                f"Ended activity: {self.current_activity.name} "
                f"({self.current_activity.duration_minutes:.1f} minutes)"
            )
        self.current_activity = None
    
    def _handle_inactivity(self) -> None:
        """Handle user inactivity."""
        if not self.current_activity:
            return
            
        inactive_time = time.time() - self.input_monitor._get_last_input_time()
        if inactive_time >= self.inactivity_threshold:
            self._end_current_activity()
    
    def get_activities(self,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Activity]:
        """Retrieve activities for the specified time range."""
        return self.storage.get_activities(start_time, end_time)
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, float]:
        """Get summary of activities for a specific date."""
        if not date:
            date = datetime.now()
            
        start_time = datetime(date.year, date.month, date.day)
        end_time = start_time + timedelta(days=1)
        
        activities = self.get_activities(start_time, end_time)
        summary = {}
        
        for activity in activities:
            if activity.process_name not in summary:
                summary[activity.process_name] = 0
            summary[activity.process_name] += activity.duration_minutes
            
        return summary
