"""
run_demo.py

Expanded demonstration that touches the planner, habits, focus sessions,
and analytics in one go.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import date, datetime, timedelta

from analytics.distraction import distraction_rate_by_task, distraction_rate_per_hour
from analytics.focuscore import compute_weekly_focus_with_grade
from analytics.weekly_report import compute_weekly_summary, format_weekly_report_text
from core.focus_session import (
    start_custom_session,
    start_habit_session,
    start_task_session,
)
from core.habit import Habit, HabitManager
from core.task import Task, TaskManager
from planner.daily_plan import generate_daily_plan


# File locations for auto-loading user-provided tasks/habits.
DATA_DIR = Path(__file__).parent
TASKS_FILE = DATA_DIR / "tasks.json"
HABITS_FILE = DATA_DIR / "habits.json"


def load_tasks_from_file(path: Path = TASKS_FILE) -> list[Task]:
    """
    Load tasks from a JSON array of objects.
    Missing/invalid fields fall back to reasonable defaults.
    """
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Could not load tasks from {path}: {exc}")
        return []

    if not isinstance(raw, list):
        print(f"Task file {path} must contain a JSON list.")
        return []

    tasks: list[Task] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        if not name:
            continue

        tasks.append(
            Task(
                name,
                item.get("duration", 25),
                category=item.get("category"),
                difficulty=item.get("difficulty", 3),
                priority=item.get("priority", 1),
                must_do_today=item.get("must_do_today", False),
                notes=item.get("notes", ""),
                pomodoro=bool(item.get("pomodoro", False)),
                planned_distractions=item.get("planned_distractions"),
            )
        )
    return tasks


def load_habits_from_file(path: Path = HABITS_FILE) -> list[Habit]:
    """Load habits from a JSON array of objects."""
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Could not load habits from {path}: {exc}")
        return []

    if not isinstance(raw, list):
        print(f"Habit file {path} must contain a JSON list.")
        return []

    habits: list[Habit] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        if not name:
            continue

        habits.append(Habit(name, frequency=item.get("frequency", "daily")))

    return habits


def prompt_str(prompt: str, default: str = "") -> str:
    """Input helper that falls back to default in non-interactive environments."""
    try:
        text = input(prompt).strip()
        return text or default
    except (OSError, EOFError):
        return default


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Ask a yes/no question with a default."""
    default_char = "y" if default else "n"
    resp = prompt_str(f"{prompt} (y/N): ", default_char).lower()
    return resp.startswith("y")


def prompt_int(prompt: str, default: int = 0, minimum: int | None = None) -> int:
    """Parse an integer with defaults and an optional lower bound."""
    raw = prompt_str(prompt, str(default))
    try:
        value = int(raw)
    except ValueError:
        value = default
    if minimum is not None:
        value = max(minimum, value)
    return value


def prompt_category() -> str | None:
    """Let the user pick a category from a small menu or type one."""
    options = ["study", "admin", "recovery", "personal", "health", "work"]
    print("Categories:")
    for idx, opt in enumerate(options, start=1):
        print(f"  {idx}. {opt}")
    choice = prompt_str("Pick category number or type custom (Enter to skip): ")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
    if choice:
        return choice
    return None


def prompt_tasks_from_user() -> list[Task]:
    """
    Ask the user to enter tasks interactively.
    First asks how many tasks to add.
    """
    if not prompt_yes_no("\nDo you want to add tasks now?", default=True):
        return []

    print("Enter tasks")
    count = prompt_int("How many tasks do you want to add? (0 to skip): ", 0, minimum=0)
    if count <= 0:
        return []

    tasks: list[Task] = []
    for idx in range(1, count + 1):
        print(f"\nTask {idx} of {count}")
        name = prompt_str("Task name: ")
        if not name:
            print("Skipped empty task name.")
            continue

        duration = prompt_int("Duration minutes (default 25): ", 25, minimum=1)
        category = prompt_category()
        difficulty = prompt_int("Difficulty 1-5 (default 3): ", 3, minimum=1)
        priority = prompt_int("Priority (default 1): ", 1, minimum=1)
        completed = prompt_yes_no("Completed?", default=False)
        pomodoro = prompt_yes_no("Use Pomodoro (25/5, zero planned distractions)?", default=False)
        planned_distractions = 0 if pomodoro else prompt_int(
            "How many distractions occurred? (default 0): ", 0, minimum=0
        )

        tasks.append(
            Task(
                name,
                duration,
                category=category,
                difficulty=difficulty,
                priority=priority,
                completed=completed,
                pomodoro=pomodoro,
                planned_distractions=planned_distractions,
                notes="pomodoro" if pomodoro else "",
            )
        )
        print("Added task.\n")
    return tasks


def prompt_habits_from_user() -> list[Habit]:
    """
    Ask the user to enter habits interactively.
    Stops when the user submits a blank habit name.
    """
    print("\nEnter habits (leave name empty to stop):")
    habits: list[Habit] = []
    while True:
        name = prompt_str("Habit name: ")
        if not name:
            break
        freq = prompt_str("Frequency (default daily): ", "daily") or "daily"
        habits.append(Habit(name, frequency=freq))
        print("Added habit.\n")
    return habits


def prompt_distractions_for_sessions(sessions) -> None:
    """
    Let the user override distraction counts for each session.
    Falls back to existing defaults if input is unavailable.
    """
    if not sessions:
        return

    print("\nDistractions per session (press Enter to keep defaults):")
    for session in sessions:
        default_val = session.distractions
        resp = prompt_str(
            f"- {session.label}: ",
            str(default_val),
        )
        try:
            session.distractions = max(0, int(resp))
        except ValueError:
            session.distractions = default_val


def build_sample_sessions(tasks: list[Task], habit: Habit):
    """Create focus sessions for every task plus a habit session."""
    now = datetime.now()
    sessions = []

    base_start = now - timedelta(hours=len(tasks))

    for idx, task in enumerate(tasks):
        session = start_task_session(task)
        session.start_time = base_start + timedelta(minutes=idx * 45)
        duration = max(10, min(task.duration, 90))
        session.end_time = session.start_time + timedelta(minutes=duration)

        if getattr(task, "pomodoro", False):
            session.notes.append("Pomodoro")

        # Use user-planned distractions when supplied; otherwise demo defaults.
        if task.planned_distractions is not None:
            session.distractions = task.planned_distractions
            session.rate_focus(5 if session.distractions == 0 else 4)
        else:
            if idx == 0:
                session.record_distraction()
                session.record_distraction()
                session.rate_focus(4)
            elif idx == 1:
                session.record_distraction()
                session.rate_focus(3)
            else:
                session.rate_focus(5)

        sessions.append(session)

    # Habit session that auto-checks in
    session_habit = start_habit_session(habit, auto_checkin=True)
    session_habit.start_time = now - timedelta(minutes=20)
    session_habit.end_session()
    session_habit.rate_focus(5)
    sessions.append(session_habit)

    return sessions


def show_plan(tasks: list[Task]) -> None:
    print("\n--- Daily plan (study mode) ---")
    blocks = generate_daily_plan(tasks, mode="study", start="09:00", end="12:00")
    for block in blocks:
        print(" ", block)


def show_analytics(sessions, habits):
    print("\n--- Analytics ---")
    week_start = date.today() - timedelta(days=date.today().weekday())

    summary = compute_weekly_summary(sessions, habits, week_start=week_start)
    score, grade = compute_weekly_focus_with_grade(
        sessions, habits, week_start=week_start
    )

    print(f"Focus score: {score:.1f} ({grade})")
    drate = distraction_rate_per_hour(sessions)
    print(f"Distractions per hour: {drate:.2f}" if drate is not None else "No time logged yet.")

    by_task = distraction_rate_by_task(sessions)
    if by_task:
        print("Distractions per hour by task:")
        for name, rate in by_task.items():
            print(f"  - {name}: {rate:.2f}")

    print("\nWeekly report text:")
    print(format_weekly_report_text(summary))


def main():
    print("\n=== Focus Pro Demo ===")

    # Tasks and task manager (prefers user-provided tasks.json; otherwise asks user)
    tasks = load_tasks_from_file()
    if not tasks:
        tasks = prompt_tasks_from_user()
    if not tasks:
        tasks = [
            Task("Study MDS", 90, category="study", difficulty=4, priority=2),
            Task("Email admin", 20, category="admin", difficulty=1),
            Task("Stretch break", 10, category="recovery", difficulty=1),
            Task("Review research notes", 45, category="study", difficulty=3),
        ]
    active_tasks = [t for t in tasks if not t.completed]
    skipped_completed = len(tasks) - len(active_tasks)
    if skipped_completed:
        print(f"\nSkipping {skipped_completed} task(s) marked completed.")

    task_manager = TaskManager()
    for t in active_tasks:
        task_manager.add_task(t)

    # Habit and habit manager (prefers habits.json; otherwise asks user)
    habit_manager = HabitManager()
    habits = load_habits_from_file()
    if not habits:
        habits = prompt_habits_from_user()
    if habits:
        for h in habits:
            habit_manager.add_habit(h)
    else:
        habit_manager.add_habit(Habit("Hydrate regularly", frequency="daily"))

    habit = habit_manager.list_habits()[0]

    show_plan(task_manager.list_tasks())

    print("\n--- Focus sessions ---")
    sessions = build_sample_sessions(task_manager.list_tasks(), habit)
    if prompt_yes_no("Do you want to enter distractions now?", default=True):
        prompt_distractions_for_sessions(sessions)
    for s in sessions:
        print(s.summary())

    show_analytics(sessions, habit_manager.list_habits())

    print("\nDemo complete.\n")


if __name__ == "__main__":
    main()
