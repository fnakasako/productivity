import psutil
from typing import Optional, Dict, Any
from .base_monitor import BaseMonitor
from AppKit import NSWorkspace

class SystemMonitor(BaseMonitor):
    """Monitors system-level activity (active window, process) on macOS."""
    
    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        try:
            # Get active application info using NSWorkspace
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            
            if not active_app:
                return None
                
            # Get process info using psutil
            pid = active_app['NSApplicationProcessIdentifier']
            process = psutil.Process(pid)
            
            return {
                'process_name': process.name(),
                'window_title': active_app['NSApplicationName'],
                'executable': process.exe(),
                'pid': pid,
                'bundle_id': active_app['NSApplicationBundleIdentifier']
            }
        except Exception:
            return None
    
    def is_active(self) -> bool:
        """Check if there's an active window."""
        return bool(self.get_current_activity())
