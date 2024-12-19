import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from .activity import Activity

class BaseStorage(ABC):
    """Abstract base class for activity storage."""
    
    @abstractmethod
    def save_activity(self, activity: Activity) -> None:
        """Save a single activity."""
        pass
    
    @abstractmethod
    def get_activities(self, 
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Activity]:
        """Retrieve activities within the specified time range."""
        pass
    
    @abstractmethod
    def cleanup_old_activities(self, days: int = 30) -> None:
        """Remove activities older than specified days."""
        pass

class JSONStorage(BaseStorage):
    """JSON file-based storage implementation."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self.filepath.write_text('[]')
    
    def save_activity(self, activity: Activity) -> None:
        activities = self._read_activities()
        activities.append(activity.to_dict())
        self._write_activities(activities)
    
    def get_activities(self,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Activity]:
        activities = self._read_activities()
        filtered_activities = []
        
        for activity_dict in activities:
            activity = Activity.from_dict(activity_dict)
            
            if start_time and activity.start_time < start_time:
                continue
            if end_time and activity.end_time and activity.end_time > end_time:
                continue
                
            filtered_activities.append(activity)
        
        return filtered_activities
    
    def cleanup_old_activities(self, days: int = 30) -> None:
        cutoff_date = datetime.now() - timedelta(days=days)
        activities = self._read_activities()
        
        filtered_activities = [
            activity for activity in activities
            if datetime.fromisoformat(activity['start_time']) > cutoff_date
        ]
        
        self._write_activities(filtered_activities)
    
    def _read_activities(self) -> List[dict]:
        with self.filepath.open('r') as f:
            return json.load(f)
    
    def _write_activities(self, activities: List[dict]) -> None:
        with self.filepath.open('w') as f:
            json.dump(activities, f, indent=2)

class SQLiteStorage(BaseStorage):
    """SQLite-based storage implementation."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(str(self.filepath)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    process_name TEXT,
                    window_title TEXT,
                    category TEXT
                )
            ''')
    
    def save_activity(self, activity: Activity) -> None:
        with sqlite3.connect(str(self.filepath)) as conn:
            conn.execute('''
                INSERT INTO activities 
                (name, start_time, end_time, process_name, window_title, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                activity.name,
                activity.start_time.isoformat(),
                activity.end_time.isoformat() if activity.end_time else None,
                activity.process_name,
                activity.window_title,
                activity.category
            ))
    
    def get_activities(self,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Activity]:
        query = 'SELECT * FROM activities'
        params = []
        conditions = []
        
        if start_time:
            conditions.append('start_time >= ?')
            params.append(start_time.isoformat())
        if end_time:
            conditions.append('end_time <= ?')
            params.append(end_time.isoformat())
            
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        with sqlite3.connect(str(self.filepath)) as conn:
            cursor = conn.execute(query, params)
            return [
                Activity(
                    name=row[1],
                    start_time=datetime.fromisoformat(row[2]),
                    end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                    process_name=row[4],
                    window_title=row[5],
                    category=row[6]
                )
                for row in cursor.fetchall()
            ]
    
    def cleanup_old_activities(self, days: int = 30) -> None:
        cutoff_date = datetime.now() - timedelta(days=days)
        with sqlite3.connect(str(self.filepath)) as conn:
            conn.execute(
                'DELETE FROM activities WHERE start_time < ?',
                (cutoff_date.isoformat(),)
            )
