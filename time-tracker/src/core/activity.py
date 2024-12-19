from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Activity:
    """Represents a single tracked activity."""
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    process_name: Optional[str] = None
    window_title: Optional[str] = None
    category: Optional[str] = None
    
    @property
    def duration_minutes(self) -> float:
        """Calculate duration in minutes."""
        if not self.end_time:
            return 0.0
        duration = (self.end_time - self.start_time).total_seconds()
        return round(duration / 60, 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "process_name": self.process_name,
            "window_title": self.window_title,
            "category": self.category,
            "duration_minutes": self.duration_minutes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Activity':
        """Create Activity from dictionary."""
        return cls(
            name=data["name"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            process_name=data.get("process_name"),
            window_title=data.get("window_title"),
            category=data.get("category")
        )
