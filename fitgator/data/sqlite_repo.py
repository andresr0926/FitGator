
"""SQLite repository skeleton (implement in Sprint 2)."""
import sqlite3
from typing import List, Optional
from ..entities import UserProfile, FoodEntry, WorkoutEntry, Goal

class SQLiteRepository:
    def __init__(self, db_path: str = "fitgator.db"):
        self.conn = sqlite3.connect(db_path)
        # TODO: create tables

    # TODO: implement required methods mirroring JsonRepository interface
