import pytest
from datetime import datetime, timedelta

from core.tasks import Task, TaskManager
from core.habit import Habit, HabitManager
from core.focus_session import (
    FocusSession,
    start_task_session,
    start_habit_session,
    start_custom_session
)

# ---------------------------------------------------------
#   TASK TESTS
# ---------------------------------------------------------

def test_task_initialization():
    t = Task("Study", duration=60, category="study")
    assert t.name == "Study"
    assert t.duration == 60
    assert t.category == "study"

def test_task_manager_add_and_list():
    m = TaskManager()
    t1 = Task("Email", 15)
    t2 = Task("Reading", 25)

    m.add_task(t1)
    m.add_task(t2)

    all_tasks = m.list_tasks()
    assert len(all_tasks) == 2
    assert all_tasks[0].name == "Email"
    assert all_tasks[1].name == "Reading"

# ---------------------------------------------------------
#   HABIT TESTS
# ---------------------------------------------------------

def test_habit_creation_and_completion():
    h = Habit("Meditation")
    assert h.streak == 0
    assert h.last_completed is None

    h.complete_today()
    assert h.streak == 1
    assert h.last_completed is not None

def test_habit_manager_add_and_list():
    hm = HabitManager()
    h1 = Habit("Exercise")
    h2 = Habit("Reading")

    hm.add_habit(h1)
    hm.add_habit(h2)

    habits = hm.list_habits()
    assert len(habits) == 2
    assert habits[0].name == "Exercise"
    assert habits[1].name == "Reading"

# ---------------------------------------------------------
#   FOCUS SESSION TESTS
# ---------------------------------------------------------

def test_focus_session_basic_flow():
    t = Task("Write report", 30)
    session = start_task_session(t)

    # Start
    assert session.task is t
    assert session.start_time is not None
    assert session.end_time is None

    # End
    session.end_session()
    assert session.end_time is not None

def test_record_distraction():
    s = FocusSession(label="Test")
    assert s.distractions == 0
    s.record_distraction()
    s.record_distraction()
    assert s.distractions == 2

def test_focus_rating():
    s = FocusSession(label="Work")
    s.rate_focus(4)
    assert s.focus_rating == 4

    with pytest.raises(ValueError):
        s.rate_focus(7)

def test_session_duration_minutes():
    s = FocusSession(label="Timer test")
    
    # Simulate end time manually for testing
    s.start_time = datetime.now() - timedelta(minutes=10)
    s.end_time = datetime.now()

    assert s.duration_minutes() == 10

def test_habit_session_auto_checkin():
    h = Habit("Stretch")
    s = start_habit_session(h, auto_checkin=True)
    s.end_session()

    # Habit should auto-complete
    assert h.streak == 1

def test_custom_session_creation():
    s = start_custom_session("Brainstorm")
    assert s.label == "Brainstorm"
    assert s.kind == "custom"

