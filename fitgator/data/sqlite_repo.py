import sqlite3
import os
from datetime import date
from typing import List, Optional

from ..entities import UserProfile, FoodEntry, WorkoutEntry, Goal


class SQLiteRepository:
    def __init__(self, db_path: str = "fitgator.db") -> None:
        full_path = os.path.abspath(db_path)
        print(f"[SQLiteRepository] Using database at: {full_path}")

        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    # --- internal helpers -------------------------------------------------

    def _create_tables(self) -> None:
        cur = self._conn.cursor()

        # Single-row profile table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                age INTEGER NOT NULL,
                weight_kg REAL NOT NULL,
                height_cm REAL NOT NULL,
                gender TEXT NOT NULL,
                activity_level REAL NOT NULL,
                units TEXT NOT NULL
            )
            """
        )

        # Single-row current goal
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                goal_type TEXT NOT NULL,
                start_date TEXT NOT NULL
            )
            """
        )

        # Food log table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                calories INTEGER NOT NULL
            )
            """
        )

        # Workout log table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                routine_name TEXT NOT NULL,
                completed INTEGER NOT NULL,
                notes TEXT NOT NULL
            )
            """
        )

        self._conn.commit()

    @staticmethod
    def _date_to_str(d: date) -> str:
        return d.isoformat()

    @staticmethod
    def _str_to_date(s: str) -> date:
        return date.fromisoformat(s)

    # --- Repository protocol methods --------------------------------------

    def load_profile(self) -> Optional[UserProfile]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM user_profile WHERE id = 1")
        row = cur.fetchone()
        if row is None:
            return None
        return UserProfile(
            age=row["age"],
            weight_kg=row["weight_kg"],
            height_cm=row["height_cm"],
            gender=row["gender"],
            activity_level=row["activity_level"],
            units=row["units"],
        )

    def save_profile(self, profile: UserProfile) -> None:
        cur = self._conn.cursor()
        # Upsert by checking existence of id=1
        cur.execute("SELECT 1 FROM user_profile WHERE id = 1")
        exists = cur.fetchone() is not None
        if exists:
            cur.execute(
                """
                UPDATE user_profile
                SET age = ?, weight_kg = ?, height_cm = ?,
                    gender = ?, activity_level = ?, units = ?
                WHERE id = 1
                """,
                (
                    profile.age,
                    profile.weight_kg,
                    profile.height_cm,
                    profile.gender,
                    profile.activity_level,
                    profile.units,
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO user_profile (
                    id, age, weight_kg, height_cm, gender, activity_level, units
                ) VALUES (1, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.age,
                    profile.weight_kg,
                    profile.height_cm,
                    profile.gender,
                    profile.activity_level,
                    profile.units,
                ),
            )
        self._conn.commit()

    def load_goal(self) -> Optional[Goal]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM goals WHERE id = 1")
        row = cur.fetchone()
        if row is None:
            return None
        return Goal(
            goal_type=row["goal_type"],
            start_date=self._str_to_date(row["start_date"]),
        )

    def save_goal(self, goal: Goal) -> None:
        cur = self._conn.cursor()
        cur.execute("SELECT 1 FROM goals WHERE id = 1")
        exists = cur.fetchone() is not None
        start_date_str = self._date_to_str(goal.start_date)
        if exists:
            cur.execute(
                """
                UPDATE goals
                SET goal_type = ?, start_date = ?
                WHERE id = 1
                """,
                (goal.goal_type, start_date_str),
            )
        else:
            cur.execute(
                """
                INSERT INTO goals (id, goal_type, start_date)
                VALUES (1, ?, ?)
                """,
                (goal.goal_type, start_date_str),
            )
        self._conn.commit()

    def load_foods(self) -> List[FoodEntry]:
        cur = self._conn.cursor()
        cur.execute("SELECT date, name, calories FROM foods ORDER BY date, id")
        rows = cur.fetchall()
        return [
            FoodEntry(
                date=self._str_to_date(row["date"]),
                name=row["name"],
                calories=row["calories"],
            )
            for row in rows
        ]

    def save_foods(self, foods: List[FoodEntry]) -> None:
        cur = self._conn.cursor()
        # For simplicity, clear and re-insert; good enough for MVP scale
        cur.execute("DELETE FROM foods")
        for entry in foods:
            cur.execute(
                "INSERT INTO foods (date, name, calories) VALUES (?, ?, ?)",
                (self._date_to_str(entry.date), entry.name, entry.calories),
            )
        self._conn.commit()

    def load_workouts(self) -> List[WorkoutEntry]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT date, routine_name, completed, notes FROM workouts ORDER BY date, id"
        )
        rows = cur.fetchall()
        return [
            WorkoutEntry(
                date=self._str_to_date(row["date"]),
                routine_name=row["routine_name"],
                completed=bool(row["completed"]),
                notes=row["notes"],
            )
            for row in rows
        ]

    def save_workouts(self, workouts: List[WorkoutEntry]) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM workouts")
        for w in workouts:
            cur.execute(
                """
                INSERT INTO workouts (date, routine_name, completed, notes)
                VALUES (?, ?, ?, ?)
                """,
                (
                    self._date_to_str(w.date),
                    w.routine_name,
                    int(w.completed),
                    w.notes,
                ),
            )
        self._conn.commit()

    # --- Extra helper for "Clear Data" feature ----------------------------

    def clear_all(self) -> None:
        """Remove all data and reset to a fresh state."""
        cur = self._conn.cursor()
        cur.execute("DELETE FROM user_profile")
        cur.execute("DELETE FROM goals")
        cur.execute("DELETE FROM foods")
        cur.execute("DELETE FROM workouts")
        self._conn.commit()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
