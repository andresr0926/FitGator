
"""Mifflin–St Jeor BMR and TDEE utilities."""
from .validation import clamp
from ..entities import UserProfile

def bmr_mifflin_st_jeor(profile: UserProfile) -> float:
    w = profile.weight_kg
    h = profile.height_cm
    a = profile.age
    # BMR
    if profile.gender == "male":
        bmr = 10*w + 6.25*h - 5*a + 5
    else:
        bmr = 10*w + 6.25*h - 5*a - 161
    return bmr

def tdee(profile: UserProfile) -> int:
    activity = clamp(profile.activity_level, 1.2, 1.9)
    return int(round(bmr_mifflin_st_jeor(profile) * activity))

def goal_adjusted_calories(profile: UserProfile, goal: str) -> int:
    base = tdee(profile)
    if goal == "cut":
        return int(round(base * 0.85))  # ~15% deficit
    if goal == "bulk":
        return int(round(base * 1.10))  # ~10% surplus
    return base
