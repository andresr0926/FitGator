
from dataclasses import dataclass
from typing import Optional, Literal
from datetime import date

UnitSystem = Literal["metric", "imperial"]
GoalType = Literal["cut", "maintain", "bulk"]

@dataclass
class UserProfile:
    age: int
    weight_kg: float
    height_cm: float
    gender: Literal["male", "female"]
    activity_level: float  # 1.2-1.9
    units: UnitSystem = "metric"

@dataclass
class Goal:
    goal_type: GoalType
    start_date: date

@dataclass
class FoodEntry:
    date: date
    name: str
    calories: int

@dataclass
class WorkoutEntry:
    date: date
    routine_name: str
    completed: bool = False
    notes: str = ""
