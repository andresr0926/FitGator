"""Mifflin–St Jeor BMR and TDEE utilities."""
from .validation import clamp
from ..entities import UserProfile


def bmr_mifflin_st_jeor(profile: UserProfile) -> float:
    """
    Compute BMR using the Mifflin–St Jeor equation.

    - If profile.units == "metric":
        weight and height are interpreted as kg / cm.
    - If profile.units == "imperial":
        weight and height are interpreted as lb / in and converted internally.
    """
    # Interpret weight/height based on unit system
    if profile.units == "imperial":
        # User stored values as lb and inches
        weight_kg = profile.weight_kg * 0.45359237
        height_cm = profile.height_cm * 2.54
    else:
        # Metric (kg, cm)
        weight_kg = profile.weight_kg
        height_cm = profile.height_cm

    a = profile.age

    if profile.gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * a + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * a - 161
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
