
from fitgator.entities import UserProfile
from fitgator.services.tdee import bmr_mifflin_st_jeor, tdee

def test_bmr_positive():
    p = UserProfile(age=30, weight_kg=70.0, height_cm=175.0, gender="male", activity_level=1.4)
    assert bmr_mifflin_st_jeor(p) > 1000

def test_tdee_monotonic_with_activity():
    p = UserProfile(age=30, weight_kg=70.0, height_cm=175.0, gender="male", activity_level=1.2)
    t1 = tdee(p)
    p.activity_level = 1.8
    t2 = tdee(p)
    assert t2 > t1
