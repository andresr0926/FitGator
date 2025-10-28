
from typing import List
from ..entities import FoodEntry, WorkoutEntry
from datetime import date

def calories_for_day(entries: List[FoodEntry], d: date) -> int:
    return sum(e.calories for e in entries if e.date == d)

def workouts_completed(entries: List[WorkoutEntry], d: date) -> int:
    return sum(1 for e in entries if e.date == d and e.completed)
