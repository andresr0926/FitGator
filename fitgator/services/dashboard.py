
from datetime import date
from typing import List, Dict
from ..entities import UserProfile, FoodEntry, WorkoutEntry
from .tdee import goal_adjusted_calories

def daily_summary(profile: UserProfile, goal: str, foods: List[FoodEntry], workouts: List[WorkoutEntry]) -> Dict[str, int]:
    today = date.today()
    target = goal_adjusted_calories(profile, goal)
    consumed = sum(e.calories for e in foods if e.date == today)
    completed = sum(1 for w in workouts if w.date == today and w.completed)
    return {
        "target_calories": target,
        "consumed_calories": consumed,
        "remaining_calories": max(0, target - consumed),
        "workouts_completed": completed
    }
