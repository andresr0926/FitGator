
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def valid_profile_fields(age: int, weight_kg: float, height_cm: float) -> bool:
    if not (10 <= age <= 100):
        return False
    if not (20.0 <= weight_kg <= 400.0):
        return False
    if not (100.0 <= height_cm <= 250.0):
        return False
    return True
