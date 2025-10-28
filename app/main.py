
from datetime import date
from fitgator.entities import UserProfile
from fitgator.services.tdee import goal_adjusted_calories
from fitgator.data.json_repo import JsonRepository

def main():
    repo = JsonRepository()
    profile = repo.load_profile()
    if not profile:
        # Demo profile
        profile = UserProfile(age=25, weight_kg=80.0, height_cm=178.0, gender="male", activity_level=1.55)
        repo.save_profile(profile)

    goal = repo.load_goal()
    if not goal:
        from fitgator.services.goals import new_goal
        goal = new_goal("maintain")
        repo.save_goal(goal)

    cals = goal_adjusted_calories(profile, goal.goal_type)
    print(f"Today's target calories for goal '{goal.goal_type}': {cals}")

if __name__ == "__main__":
    main()
