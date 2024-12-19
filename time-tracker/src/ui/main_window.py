import tkinter as tk
from tkinter import ttk
from typing import Optional
from datetime import datetime, timedelta
import yaml
import logging
from pathlib import Path
from ..core.tracker import ActivityTracker

logger = logging.getLogger(__name__)

class MainWindow:
    """Main application window."""
    
    def __init__(self, config: dict):
        self.config = config
        self.tracker: Optional[ActivityTracker] = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(config['ui']['window_title'])
        self.root.geometry(config['ui']['window_size'])
        
        self._setup_ui()
        self._setup_tracker()
        self._setup_update_timer()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Current Activity", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Not tracking",
            wraplength=400
        )
        self.status_label.pack(fill=tk.X)
        
        # Controls Frame
        controls_frame = ttk.Frame(self.root, padding=5)
        controls_frame.pack(fill=tk.X, padx=5)
        
        self.start_button = ttk.Button(
            controls_frame,
            text="Start Tracking",
            command=self._toggle_tracking
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Recent Activities Frame
        activities_frame = ttk.LabelFrame(
            self.root,
            text="Recent Activities",
            padding=10
        )
        activities_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for activities
        self.activities_tree = ttk.Treeview(
            activities_frame,
            columns=("Duration", "Application"),
            show="headings",
            selectmode="none"
        )
        
        self.activities_tree.heading("Duration", text="Duration")
        self.activities_tree.heading("Application", text="Application")
        
        self.activities_tree.column("Duration", width=100)
        self.activities_tree.column("Application", width=300)
        
        scrollbar = ttk.Scrollbar(
            activities_frame,
            orient=tk.VERTICAL,
            command=self.activities_tree.yview
        )
        self.activities_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activities_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_tracker(self):
        """Initialize the activity tracker."""
        try:
            self.tracker = ActivityTracker(self.config)
        except Exception as e:
            logger.error(f"Failed to initialize tracker: {e}", exc_info=True)
            self.status_label.config(
                text="Error: Failed to initialize activity tracking"
            )
            self.start_button.config(state=tk.DISABLED)
    
    def _setup_update_timer(self):
        """Setup timer for periodic UI updates."""
        def update():
            self._update_current_activity()
            self._update_recent_activities()
            self.root.after(1000, update)  # Update every second
        
        self.root.after(1000, update)
    
    def _toggle_tracking(self):
        """Toggle activity tracking on/off."""
        if not self.tracker:
            return
            
        if self.start_button.cget("text") == "Start Tracking":
            self.tracker.start()
            self.start_button.config(text="Stop Tracking")
            logger.info("Tracking started")
        else:
            self.tracker.stop()
            self.start_button.config(text="Start Tracking")
            self.status_label.config(text="Not tracking")
            logger.info("Tracking stopped")
    
    def _update_current_activity(self):
        """Update the current activity display."""
        if not self.tracker or not self.tracker.current_activity:
            return
            
        current = self.tracker.current_activity
        duration = datetime.now() - current.start_time
        minutes = duration.total_seconds() / 60
        
        status_text = (
            f"Current: {current.window_title}\n"
            f"Application: {current.process_name}\n"
            f"Duration: {minutes:.1f} minutes"
        )
        self.status_label.config(text=status_text)
    
    def _update_recent_activities(self):
        """Update the recent activities list."""
        if not self.tracker:
            return
            
        # Clear current items
        for item in self.activities_tree.get_children():
            self.activities_tree.delete(item)
        
        # Get recent activities
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        activities = self.tracker.get_activities(start_time, end_time)
        
        # Sort by start time, most recent first
        activities.sort(key=lambda x: x.start_time, reverse=True)
        
        # Take only the most recent N activities
        limit = self.config['ui']['recent_activities_count']
        for activity in activities[:limit]:
            self.activities_tree.insert(
                "",
                tk.END,
                values=(
                    f"{activity.duration_minutes:.1f} min",
                    f"{activity.process_name}: {activity.window_title}"
                )
            )
    
    def run(self):
        """Start the main application loop."""
        self.root.mainloop()
        
        # Cleanup
        if self.tracker:
            self.tracker.stop()

def main():
    """Main entry point for the UI."""
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent.parent / 'config' / 'default_config.yaml'
        with config_path.open('r') as f:
            config = yaml.safe_load(f)
        
        # Setup logging
        logging_config_path = config_path.parent / 'logging_config.yaml'
        with logging_config_path.open('r') as f:
            logging_config = yaml.safe_load(f)
            logging.config.dictConfig(logging_config)
        
        # Create and run main window
        window = MainWindow(config)
        window.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
