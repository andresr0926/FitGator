import tkinter as tk
import os
from tkinter import ttk, messagebox
from datetime import date
from typing import List
import csv

from fitgator.entities import UserProfile, FoodEntry, WorkoutEntry, Goal
from fitgator.services.goals import new_goal
from fitgator.services.dashboard import daily_summary
from fitgator.data.sqlite_repo import SQLiteRepository

ACTIVITY_OPTIONS = [
    ("Sedentary (little or no exercise)", 1.2),
    ("Light exercise (1–3 days/week)", 1.375),
    ("Moderate exercise (3–5 days/week)", 1.55),
    ("Heavy exercise (6–7 days/week)", 1.725),
    ("Athlete (2x per day)", 1.9),
]

WORKOUT_PLANS = {
    "Beginner Full Body (3 days)": [
        "Bodyweight squats – 3 x 10",
        "Push-ups – 3 x 8",
        "Glute bridges – 3 x 12",
        "Plank – 3 x 30 seconds",
    ],
    "Push / Pull / Legs (3 days)": [
        "Push day: Bench press or push-ups – 3 x 8–10",
        "Push day: Shoulder press – 3 x 10",
        "Pull day: Rows – 3 x 10",
        "Pull day: Lat pulldown or assisted pull-ups – 3 x 8–10",
        "Leg day: Squats – 3 x 8–10",
        "Leg day: Lunges – 3 x 10 per leg",
    ],
    "Home Bodyweight (4 days)": [
        "Jumping jacks – 3 x 30 sec",
        "Push-ups – 3 x 8–10",
        "Bodyweight squats – 3 x 12",
        "Glute bridges – 3 x 15",
        "Hip thrusts – 3 x 12",
        "Plank – 3 x 30–45 sec",
    ],
}


class FitGatorApp(tk.Tk):
    """Tkinter-based GUI for the FitGator MVP."""

    def __init__(self, repo: SQLiteRepository) -> None:
        super().__init__()
        self.title("FitGator")
        self.geometry("800x600")

        self._repo = repo

        # In-memory cached lists for foods and workouts
        self._foods: List[FoodEntry] = self._repo.load_foods()
        self._workouts: List[WorkoutEntry] = self._repo.load_workouts()

        self._profile: UserProfile | None = self._repo.load_profile()
        self._goal: Goal | None = self._repo.load_goal()

        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.profile_frame = ttk.Frame(notebook, padding=10)
        self.goal_frame = ttk.Frame(notebook, padding=10)
        self.calorie_frame = ttk.Frame(notebook, padding=10)
        self.workout_frame = ttk.Frame(notebook, padding=10)
        self.dashboard_frame = ttk.Frame(notebook, padding=10)
        self.settings_frame = ttk.Frame(notebook, padding=10)

        notebook.add(self.profile_frame, text="Profile")
        notebook.add(self.goal_frame, text="Goal")
        notebook.add(self.calorie_frame, text="Calories")
        notebook.add(self.workout_frame, text="Workouts")
        notebook.add(self.dashboard_frame, text="Dashboard")
        notebook.add(self.settings_frame, text="Settings")

        self._build_profile_tab()
        self._build_goal_tab()
        self._build_calorie_tab()
        self._build_workout_tab()
        self._build_dashboard_tab()
        self._build_settings_tab()

    # ---------------------------- Profile tab --------------------------

    def _build_profile_tab(self) -> None:
        f = self.profile_frame

        ttk.Label(f, text="Age:").grid(row=0, column=0, sticky="w")
        ttk.Label(f, text="Weight:").grid(row=1, column=0, sticky="w")
        ttk.Label(f, text="Height:").grid(row=2, column=0, sticky="w")
        ttk.Label(f, text="Gender (male/female):").grid(row=3, column=0, sticky="w")
        ttk.Label(f, text="Units:").grid(row=4, column=0, sticky="w")
        ttk.Label(f, text="Activity Level:").grid(row=5, column=0, sticky="w")

        self.age_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.gender_var = tk.StringVar()

        # "metric" = kg/cm, "imperial" = lb/in
        self.unit_var = tk.StringVar(value="metric")

        # Activity dropdown (TDEE-style)
        self.activity_level_var = tk.StringVar()

        ttk.Entry(f, textvariable=self.age_var).grid(row=0, column=1, sticky="ew")
        ttk.Entry(f, textvariable=self.weight_var).grid(row=1, column=1, sticky="ew")
        ttk.Entry(f, textvariable=self.height_var).grid(row=2, column=1, sticky="ew")
        ttk.Entry(f, textvariable=self.gender_var).grid(row=3, column=1, sticky="ew")

        units_box = ttk.Combobox(
            f,
            textvariable=self.unit_var,
            values=["metric", "imperial"],
            state="readonly",
        )
        units_box.grid(row=4, column=1, sticky="ew")

        activity_labels = [label for (label, _mult) in ACTIVITY_OPTIONS]
        activity_box = ttk.Combobox(
            f,
            textvariable=self.activity_level_var,
            values=activity_labels,
            state="readonly",
        )
        activity_box.grid(row=5, column=1, sticky="ew")

        f.columnconfigure(1, weight=1)

        ttk.Button(f, text="Save Profile", command=self._save_profile).grid(
            row=6, column=0, columnspan=2, pady=10
        )

        # Populate from existing profile if any
        if self._profile:
            self.age_var.set(str(self._profile.age))
            # IMPORTANT: we do NOT convert; we just show what’s stored
            self.weight_var.set(f"{self._profile.weight_kg:.1f}")
            self.height_var.set(f"{self._profile.height_cm:.1f}")
            self.gender_var.set(self._profile.gender)
            self.unit_var.set(self._profile.units)

            # Pick closest activity label based on stored multiplier
            stored_mult = self._profile.activity_level
            closest_label = ACTIVITY_OPTIONS[0][0]
            closest_diff = abs(stored_mult - ACTIVITY_OPTIONS[0][1])
            for label, mult in ACTIVITY_OPTIONS[1:]:
                diff = abs(stored_mult - mult)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_label = label
            self.activity_level_var.set(closest_label)
        else:
            # Defaults for a new profile
            self.unit_var.set("metric")
            self.activity_level_var.set("Moderate exercise (3–5 days/week)")

    def _save_profile(self) -> None:
        try:
            age = int(self.age_var.get())
            weight_input = float(self.weight_var.get())
            height_input = float(self.height_var.get())
            gender = self.gender_var.get().strip().lower()
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numeric values for age, weight, and height."
            )
            return

        if gender not in ("male", "female"):
            messagebox.showerror("Error", "Gender must be 'male' or 'female'.")
            return

        unit_system = self.unit_var.get() or "metric"

        # Map activity label -> multiplier
        activity_label = self.activity_level_var.get()
        activity_multiplier = None
        for label, mult in ACTIVITY_OPTIONS:
            if label == activity_label:
                activity_multiplier = mult
                break
        if activity_multiplier is None:
            activity_multiplier = 1.55  # default moderate

        # NO conversion here – we store the value exactly as entered.
        # TDEE will interpret based on profile.units.
        profile = UserProfile(
            age=age,
            weight_kg=weight_input,  # semantic: "weight value"
            height_cm=height_input,  # semantic: "height value"
            gender=gender,  # type: ignore[arg-type]
            activity_level=activity_multiplier,
            units=unit_system,  # "metric" or "imperial"
        )
        self._repo.save_profile(profile)
        print("SAVED PROFILE TO:", os.path.abspath("fitgator.db"))
        self._profile = profile
        messagebox.showinfo("Saved", "Profile saved successfully.")
        self._refresh_dashboard()

    # ---------------------------- Goal tab -----------------------------

    def _build_goal_tab(self) -> None:
        f = self.goal_frame

        ttk.Label(f, text="Select Goal:").grid(row=0, column=0, sticky="w")

        self.goal_var = tk.StringVar(value="maintain")
        ttk.Radiobutton(
            f, text="Cut", variable=self.goal_var, value="cut"
        ).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(
            f, text="Maintain", variable=self.goal_var, value="maintain"
        ).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(
            f, text="Bulk", variable=self.goal_var, value="bulk"
        ).grid(row=3, column=0, sticky="w")

        ttk.Button(f, text="Save Goal", command=self._save_goal).grid(
            row=4, column=0, pady=10
        )

        if self._goal:
            self.goal_var.set(self._goal.goal_type)

    def _save_goal(self) -> None:
        goal_type = self.goal_var.get()
        goal = new_goal(goal_type)  # uses today's date
        self._repo.save_goal(goal)
        self._goal = goal
        messagebox.showinfo("Saved", f"Goal set to '{goal_type}'.")
        self._refresh_dashboard()

    # -------------------------- Calories tab ---------------------------

    def _build_calorie_tab(self) -> None:
        f = self.calorie_frame

        ttk.Label(f, text="Food name:").grid(row=0, column=0, sticky="w")
        ttk.Label(f, text="Calories:").grid(row=1, column=0, sticky="w")

        self.food_name_var = tk.StringVar()
        self.food_cal_var = tk.StringVar()

        ttk.Entry(f, textvariable=self.food_name_var).grid(row=0, column=1, sticky="ew")
        ttk.Entry(f, textvariable=self.food_cal_var).grid(row=1, column=1, sticky="ew")

        ttk.Button(f, text="Add Entry", command=self._add_food_entry).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        ttk.Label(f, text="Today's entries:").grid(row=3, column=0, sticky="w")
        self.food_listbox = tk.Listbox(f, height=10)
        self.food_listbox.grid(row=4, column=0, columnspan=2, sticky="nsew")

        ttk.Button(f, text="Delete Selected", command=self._delete_food_entry).grid(
            row=5, column=0, columnspan=2, pady=5
        )

        f.rowconfigure(4, weight=1)
        f.columnconfigure(1, weight=1)

        self._refresh_food_list()

    def _add_food_entry(self) -> None:
        name = self.food_name_var.get().strip()
        cal_str = self.food_cal_var.get().strip()
        if not name or not cal_str:
            messagebox.showerror("Error", "Please enter both name and calories.")
            return
        try:
            calories = int(cal_str)
        except ValueError:
            messagebox.showerror("Error", "Calories must be an integer.")
            return

        entry = FoodEntry(date=date.today(), name=name, calories=calories)
        self._foods.append(entry)
        self._repo.save_foods(self._foods)
        self.food_name_var.set("")
        self.food_cal_var.set("")
        self._refresh_food_list()
        self._refresh_dashboard()

    def _refresh_food_list(self) -> None:
        self.food_listbox.delete(0, tk.END)
        today = date.today()
        for entry in self._foods:
            if entry.date == today:
                self.food_listbox.insert(
                    tk.END, f"{entry.name} - {entry.calories} kcal"
                )

    def _delete_food_entry(self) -> None:
        idx = self.food_listbox.curselection()
        if not idx:
            return
        # Map visible index back to underlying list index by filtering today's entries
        today = date.today()
        today_entries = [e for e in self._foods if e.date == today]
        selected = today_entries[idx[0]]
        # Remove the selected entry object from the full list
        self._foods = [e for e in self._foods if e is not selected]
        self._repo.save_foods(self._foods)
        self._refresh_food_list()
        self._refresh_dashboard()

    # -------------------------- Workouts tab ---------------------------

    def _build_workout_tab(self) -> None:
        f = self.workout_frame

        # Manual workout entry
        ttk.Label(f, text="Workout name:").grid(row=0, column=0, sticky="w")
        self.workout_name_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.workout_name_var).grid(
            row=0, column=1, sticky="ew"
        )

        self.workout_completed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            f, text="Completed", variable=self.workout_completed_var
        ).grid(row=1, column=0, columnspan=2, sticky="w")

        ttk.Button(f, text="Add Workout", command=self._add_workout).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        # Suggested plan UI
        ttk.Label(f, text="Suggested plans (optional):").grid(
            row=3, column=0, sticky="w", pady=(10, 0)
        )

        self.workout_plan_var = tk.StringVar()
        self.workout_plan_box = ttk.Combobox(
            f,
            textvariable=self.workout_plan_var,
            values=list(WORKOUT_PLANS.keys()),
            state="readonly",
        )
        self.workout_plan_box.grid(row=3, column=1, sticky="ew", pady=(10, 0))
        self.workout_plan_box.bind("<<ComboboxSelected>>", self._on_plan_selected)

        self.plan_preview_var = tk.StringVar(
            value="Select a plan to see today's suggested exercises."
        )
        ttk.Label(
            f,
            textvariable=self.plan_preview_var,
            wraplength=500,
            justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 4))

        ttk.Button(
            f,
            text="Add Plan to Today's Workouts",
            command=self._add_plan_to_workouts,
        ).grid(row=5, column=0, columnspan=2, pady=(4, 10))

        # Existing list of today's workouts
        ttk.Label(f, text="Today's workouts:").grid(row=6, column=0, sticky="w")
        self.workout_listbox = tk.Listbox(f, height=8)
        self.workout_listbox.grid(row=7, column=0, columnspan=2, sticky="nsew")

        f.rowconfigure(7, weight=1)
        f.columnconfigure(1, weight=1)

        self._refresh_workout_list()

    def _add_workout(self) -> None:
        name = self.workout_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a routine name.")
            return
        entry = WorkoutEntry(
            date=date.today(),
            routine_name=name,
            completed=self.workout_completed_var.get(),
            notes="",
        )
        self._workouts.append(entry)
        self._repo.save_workouts(self._workouts)
        self.workout_name_var.set("")
        self._refresh_workout_list()
        self._refresh_dashboard()

    def _refresh_workout_list(self) -> None:
        self.workout_listbox.delete(0, tk.END)
        today = date.today()
        for w in self._workouts:
            if w.date == today:
                status = "✅" if w.completed else "❌"
                self.workout_listbox.insert(
                    tk.END, f"{status} {w.routine_name}"
                )

    def _on_plan_selected(self, event=None) -> None:
        plan_name = self.workout_plan_var.get()
        exercises = WORKOUT_PLANS.get(plan_name)
        if not exercises:
            self.plan_preview_var.set(
                "Select a plan to see today's suggested exercises."
            )
            return

        lines = [f"- {e}" for e in exercises]
        self.plan_preview_var.set("\n".join(lines))

    def _add_plan_to_workouts(self) -> None:
        plan_name = self.workout_plan_var.get()
        exercises = WORKOUT_PLANS.get(plan_name)
        if not exercises:
            messagebox.showerror("Error", "Please select a workout plan first.")
            return

        today = date.today()
        added = 0
        for exercise in exercises:
            entry = WorkoutEntry(
                date=today,
                routine_name=exercise,
                completed=True,
                notes=f"Plan: {plan_name}",
            )
            self._workouts.append(entry)
            added += 1

        self._repo.save_workouts(self._workouts)
        self._refresh_workout_list()
        self._refresh_dashboard()

        messagebox.showinfo(
            "Plan added",
            f"Added {added} workouts for plan '{plan_name}' to today.",
        )

    # -------------------------- Dashboard tab --------------------------

    def _build_dashboard_tab(self) -> None:
        f = self.dashboard_frame

        self.target_var = tk.StringVar(value="0")
        self.consumed_var = tk.StringVar(value="0")
        self.remaining_var = tk.StringVar(value="0")
        self.workouts_done_var = tk.StringVar(value="0")

        ttk.Label(f, text="Today's Target:").grid(row=0, column=0, sticky="w")
        ttk.Label(f, textvariable=self.target_var).grid(row=0, column=1, sticky="w")

        ttk.Label(f, text="Consumed:").grid(row=1, column=0, sticky="w")
        ttk.Label(f, textvariable=self.consumed_var).grid(row=1, column=1, sticky="w")

        ttk.Label(f, text="Remaining:").grid(row=2, column=0, sticky="w")
        ttk.Label(f, textvariable=self.remaining_var).grid(
            row=2, column=1, sticky="w"
        )

        ttk.Label(f, text="Workouts Completed:").grid(row=3, column=0, sticky="w")
        ttk.Label(f, textvariable=self.workouts_done_var).grid(
            row=3, column=1, sticky="w"
        )

        ttk.Button(f, text="Refresh", command=self._refresh_dashboard).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        for i in range(2):
            f.columnconfigure(i, weight=1)

        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        if not (self._profile and self._goal):
            self.target_var.set("Set profile & goal first")
            self.consumed_var.set("0")
            self.remaining_var.set("0")
            self.workouts_done_var.set("0")
            return

        summary = daily_summary(
            self._profile,
            self._goal.goal_type,
            self._foods,
            self._workouts,
        )
        self.target_var.set(str(summary["target_calories"]))
        self.consumed_var.set(str(summary["consumed_calories"]))
        self.remaining_var.set(str(summary["remaining_calories"]))
        self.workouts_done_var.set(str(summary["workouts_completed"]))

    # -------------------------- Settings tab ---------------------------

    def _build_settings_tab(self) -> None:
        f = self.settings_frame

        # Title / header
        ttk.Label(
            f,
            text="Data & Settings",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(pady=(10, 5))

        # Export button
        ttk.Button(
            f,
            text="Export Data to CSV",
            command=self._export_data_csv,
        ).pack(pady=5)

        # Clear data button
        ttk.Button(
            f,
            text="Clear All Data",
            command=self._clear_data_confirm,
        ).pack(pady=20)

    def _clear_data_confirm(self) -> None:
        if not messagebox.askyesno(
            "Confirm", "This will delete ALL local data. Continue?"
        ):
            return
        self._repo.clear_all()
        self._profile = None
        self._goal = None
        self._foods.clear()
        self._workouts.clear()
        # Clear UI
        self.age_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.gender_var.set("")
        self.unit_var.set("metric")
        self.activity_level_var.set("Moderate exercise (3–5 days/week)")
        self.goal_var.set("maintain")
        self._refresh_food_list()
        self._refresh_workout_list()
        self._refresh_dashboard()
        messagebox.showinfo("Done", "All data cleared.")

    def _export_data_csv(self) -> None:
        """Export all foods and workouts to a CSV file."""
        try:
            foods = self._repo.load_foods()
            workouts = self._repo.load_workouts()
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not load data:\n{e}")
            return

        export_path = "fitgator_export.csv"

        try:
            with open(export_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["type", "date", "name", "calories", "completed", "notes"]
                )

                # Food entries
                for food in foods:
                    writer.writerow(
                        [
                            "food",
                            food.date.isoformat(),
                            food.name,
                            food.calories,
                            "",
                            "",
                        ]
                    )

                # Workout entries
                for w in workouts:
                    writer.writerow(
                        [
                            "workout",
                            w.date.isoformat(),
                            w.routine_name,
                            "",
                            "yes" if w.completed else "no",
                            getattr(w, "notes", ""),
                        ]
                    )

            messagebox.showinfo(
                "Export complete",
                f"Data exported to {export_path} in the current folder.",
            )
        except OSError as e:
            messagebox.showerror(
                "Export failed",
                f"Could not write export file:\n{e}"
            )
