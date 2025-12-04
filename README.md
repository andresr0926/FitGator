# FitGator – Lightweight Fitness & Nutrition Tracker

**Group Name:** FitGator  
**Group Number:** 13  
**Team Member:** Andres Rodriguez

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/andresr0926/FitGator)

---

FitGator is a lightweight fitness and nutrition tracker designed for students and busy adults. It provides personalized calorie targets based on TDEE, daily calorie logging, workout tracking, and a simple dashboard—all stored locally with no login or online requirements.

---

## Features

### Profile Management
- Enter age, weight, height, gender, units (metric/imperial), and activity level
- Input validation ensures data quality
- Saved automatically to SQLite

### Goal Selection & TDEE Calculation
- Choose from three goals: **Cut**, **Maintain**, or **Bulk**
- Uses the Mifflin–St Jeor equation for BMR/TDEE calculation
- Adjusts calorie target dynamically based on your goal

### Calorie Logging
- Add food entries for the current day
- Delete entries easily

### Workout Tracking
- Log workouts and mark them as complete or incomplete

### Dashboard
- View today's calorie target, calories consumed, remaining calories, and completed workouts at a glance

### Data Persistence & Settings
- All data stored in local SQLite database
- "Clear Data" option resets the entire app

---

## Architecture Overview

FitGator follows a **three-layer architecture**:

| Layer | Responsibility |
|-------|----------------|
| **Presentation** | User interface (Tkinter) |
| **Application** | Business logic and calculations |
| **Data** | SQLite database operations |

---

## Requirements

- Python 3.10+
- pip
- Tkinter (usually included with Python)

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/andresr0926/FitGator.git
cd FitGator

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Application

```bash
python -m app.main
```

---

## Running Tests

```bash
pytest
```

---

## Data Storage & Privacy

FitGator uses **local-only storage** via SQLite. Your data never leaves your device, and the app is fully functional offline.

---

## Known Limitations

- No long-term analytics or historical trends
- CSV export is planned for a future release

---

## License

This project is for **educational use only**.