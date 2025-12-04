
import json
from dataclasses import asdict
from datetime import date
from typing import List, Optional
from pathlib import Path
from ..entities import UserProfile, FoodEntry, WorkoutEntry, Goal

def _date_default(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def _date_parse(s: str) -> date:
    return date.fromisoformat(s)

class JsonRepository:
    def __init__(self, path: str = "fitgator_data.json"):
        self.path = Path(path)
        if not self.path.exists():
            self._write({"profile": None, "goal": None, "foods": [], "workouts": []})

    def _read(self):
        return json.loads(self.path.read_text())

    def _write(self, obj):
        self.path.write_text(json.dumps(obj, default=_date_default, indent=2))

    def load_profile(self) -> Optional[UserProfile]:
        raw = self._read()["profile"]
        if not raw:
            return None
        return UserProfile(**raw)

    def save_profile(self, profile: UserProfile) -> None:
        data = self._read()
        data["profile"] = asdict(profile)
        self._write(data)

    def load_goal(self) -> Optional[Goal]:
        raw = self._read()["goal"]
        if not raw:
            return None
        raw["start_date"] = _date_parse(raw["start_date"])
        return Goal(**raw)

    def save_goal(self, goal: Goal) -> None:
        data = self._read()
        g = asdict(goal)
        data["goal"] = g
        self._write(data)

    def load_foods(self) -> List[FoodEntry]:
        data = self._read()["foods"]
        res: List[FoodEntry] = []
        for f in data:
            f["date"] = _date_parse(f["date"])
            res.append(FoodEntry(**f))
        return res

    def save_foods(self, foods: List[FoodEntry]) -> None:
        data = self._read()
        data["foods"] = [asdict(f) for f in foods]
        self._write(data)

    def load_workouts(self) -> List[WorkoutEntry]:
        data = self._read()["workouts"]
        res: List[WorkoutEntry] = []
        for w in data:
            w["date"] = _date_parse(w["date"])
            res.append(WorkoutEntry(**w))
        return res

    def save_workouts(self, workouts: List[WorkoutEntry]) -> None:
        data = self._read()
        data["workouts"] = [asdict(w) for w in workouts]
        self._write(data)
