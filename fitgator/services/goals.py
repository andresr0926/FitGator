
from ..entities import Goal, GoalType
from datetime import date

def new_goal(goal_type: GoalType) -> Goal:
    return Goal(goal_type=goal_type, start_date=date.today())
