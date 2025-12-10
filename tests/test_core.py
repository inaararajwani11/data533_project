import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

import core.task as task_module
from core.focus_session import (
    FocusSession,
    start_custom_session,
    start_habit_session,
    start_task_session,
)
from core.habit import Habit, HabitManager
from core.task import Task as AliasTask, TaskManager as AliasTaskManager
from core.tasks import Task, TaskManager


class TestTasksModule(unittest.TestCase):
    """Tests for the core.tasks module."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.deadline = date.today() + timedelta(days=3)

    def setUp(self) -> None:
        self.task = Task(
            "Write report",
            duration="45",
            priority="2",
            difficulty=10,
            deadline=self.deadline,
            planned_distractions="3",
            pomodoro=True,
        )
        self.manager = TaskManager()
        self.manager.add_task(Task("Email admin", 15))

    def tearDown(self) -> None:
        self.manager.tasks.clear()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.deadline = None

    def test_task_initialization(self) -> None:
        task = Task("Study", duration=60, category="study")
        self.assertEqual(task.name, "Study")
        self.assertEqual(task.duration, 60)
        self.assertEqual(task.category, "study")

    def test_task_manager_add_and_list(self) -> None:
        manager = TaskManager()
        first = Task("Email", 15)
        second = Task("Reading", 25)
        manager.add_task(first)
        manager.add_task(second)
        all_tasks = manager.list_tasks()
        self.assertEqual(len(all_tasks), 2)
        self.assertEqual(all_tasks[0].name, "Email")
        self.assertEqual(all_tasks[1].name, "Reading")

    def test_task_normalization_and_summary(self) -> None:
        summary = self.task.summary()
        self.assertEqual(self.task.duration, 45)
        self.assertEqual(self.task.difficulty, 5)
        self.assertEqual(self.task.priority, 2)
        self.assertEqual(self.task.planned_distractions, 3)
        self.assertIn("Write report", summary)
        self.assertIn("45 min", summary)

    def test_task_manager_operations(self) -> None:
        second = Task("Read chapter", duration=30, must_do_today=True)
        self.manager.add_task(self.task)
        self.manager.add_task(second)

        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].name, "Email admin")
        self.assertIs(tasks[1], self.task)
        self.assertEqual(self.manager.next_task().name, "Email admin")
        self.assertTrue(self.manager.remove_task("Email admin"))
        self.assertEqual(len(self.manager.list_tasks()), 2)
        self.assertFalse(self.manager.remove_task("Not here"))


class TestHabitModule(unittest.TestCase):
    """Tests for the core.habit module."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.today = date.today()
        cls.yesterday = cls.today - timedelta(days=1)

    def setUp(self) -> None:
        self.habit = Habit(
            "Morning run",
            frequency="daily",
            streak=2,
            last_completed=self.yesterday,
        )
        self.manager = HabitManager()
        self.manager.add_habit(self.habit)

    def tearDown(self) -> None:
        self.manager.habits.clear()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.today = None
        cls.yesterday = None

    def test_complete_today_and_due_flags(self) -> None:
        self.assertTrue(self.habit.is_due())
        self.habit.complete_today()
        self.assertEqual(self.habit.streak, 3)
        self.assertEqual(self.habit.last_completed, self.today)
        self.assertFalse(self.habit.is_due())
        self.habit.complete_today()
        self.assertEqual(self.habit.streak, 3)

    def test_habit_manager_add_list_and_checkin(self) -> None:
        extra = Habit("Stretching", streak=1, last_completed=self.yesterday)
        self.manager.add_habit(extra)
        self.assertEqual(len(self.manager.list_habits()), 2)
        self.assertEqual(self.manager.list_habits()[1].name, "Stretching")

        with patch("core.habit.input", side_effect=["1"]):
            self.manager.checkin()

        habits = self.manager.list_habits()
        self.assertEqual(len(habits), 2)
        self.assertEqual(habits[0].name, "Morning run")
        self.assertFalse(habits[0].is_due())
        self.assertTrue(habits[1].is_due())

    def test_habit_creation_and_completion(self) -> None:
        habit = Habit("Meditation")
        self.assertEqual(habit.streak, 0)
        self.assertIsNone(habit.last_completed)
        habit.complete_today()
        self.assertEqual(habit.streak, 1)
        self.assertIsNotNone(habit.last_completed)

    def test_habit_manager_add_and_list(self) -> None:
        habit_manager = HabitManager()
        habit_manager.add_habit(Habit("Exercise"))
        habit_manager.add_habit(Habit("Reading"))
        habits = habit_manager.list_habits()
        self.assertEqual(len(habits), 2)
        self.assertEqual(habits[0].name, "Exercise")
        self.assertEqual(habits[1].name, "Reading")


class TestFocusSessionModule(unittest.TestCase):
    """Tests for the core.focus_session module."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.today = date.today()
        cls.yesterday = cls.today - timedelta(days=1)

    def setUp(self) -> None:
        self.task = Task("Deep work", duration=50)
        self.habit = Habit("Evening stretch", streak=1, last_completed=self.yesterday)
        self.session: FocusSession | None = None

    def tearDown(self) -> None:
        self.session = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.today = None
        cls.yesterday = None

    def test_task_session_lifecycle(self) -> None:
        self.session = start_task_session(self.task)
        self.session.start_time -= timedelta(minutes=2)
        self.assertEqual(self.session.kind, "task")
        self.assertEqual(self.session.label, self.task.name)
        self.assertIsNone(self.session.end_time)
        self.assertIsNone(self.session.duration_minutes())
        self.session.end_session()
        self.assertIsNotNone(self.session.end_time)
        self.assertIsInstance(self.session.duration_minutes(), int)
        self.assertGreaterEqual(self.session.duration_minutes(), 1)
        summary = self.session.summary()
        self.assertEqual(summary["label"], self.task.name)
        self.assertEqual(summary["kind"], "task")

    def test_focus_session_basic_flow(self) -> None:
        session = start_task_session(self.task)
        self.assertIs(session.task, self.task)
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)
        session.end_session()
        self.assertIsNotNone(session.end_time)

    def test_habit_session_notes_distractions_and_checkin(self) -> None:
        self.session = start_habit_session(self.habit)
        self.session.record_distraction()
        self.session.record_distraction()
        self.session.add_note("Kept focus")
        self.session.add_note("Small break needed")
        self.session.rate_focus(4)
        self.session.end_session()
        self.assertEqual(self.session.kind, "habit")
        self.assertEqual(self.session.label, self.habit.name)
        self.assertEqual(self.session.distractions, 2)
        self.assertEqual(len(self.session.notes), 2)
        self.assertEqual(self.session.focus_rating, 4)
        self.assertEqual(self.habit.last_completed, self.today)
        self.assertEqual(self.habit.streak, 2)

    def test_record_distraction(self) -> None:
        session = FocusSession(label="Test")
        self.assertEqual(session.distractions, 0)
        session.record_distraction()
        session.record_distraction()
        self.assertEqual(session.distractions, 2)

    def test_focus_rating(self) -> None:
        session = FocusSession(label="Work")
        session.rate_focus(4)
        self.assertEqual(session.focus_rating, 4)
        with self.assertRaises(ValueError):
            session.rate_focus(7)

    def test_session_duration_minutes(self) -> None:
        session = FocusSession(label="Timer test")
        session.start_time = datetime.now() - timedelta(minutes=10)
        session.end_time = datetime.now()
        self.assertEqual(session.duration_minutes(), 10)

    def test_habit_session_auto_checkin(self) -> None:
        habit = Habit("Stretch")
        session = start_habit_session(habit, auto_checkin=True)
        session.end_session()
        self.assertEqual(habit.streak, 1)

    def test_custom_session_creation(self) -> None:
        session = start_custom_session("Brainstorm")
        self.assertEqual(session.label, "Brainstorm")
        self.assertEqual(session.kind, "custom")


class TestTaskAliasModule(unittest.TestCase):
    """Tests for the lightweight core.task re-export module."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks_task_cls = Task
        cls.tasks_manager_cls = TaskManager

    def setUp(self) -> None:
        self.alias_task = AliasTask("Alias task", duration=20, difficulty="4")
        self.manager = AliasTaskManager()

    def tearDown(self) -> None:
        self.manager.tasks.clear()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tasks_task_cls = None
        cls.tasks_manager_cls = None

    def test_reexports_and_dunder_all(self) -> None:
        self.assertIn("Task", task_module.__all__)
        self.assertIn("TaskManager", task_module.__all__)
        self.assertEqual(len(task_module.__all__), 2)
        self.assertIs(task_module.Task, self.tasks_task_cls)
        self.assertIs(task_module.TaskManager, self.tasks_manager_cls)

    def test_task_manager_usage_from_alias(self) -> None:
        second = AliasTask("Second", duration="25", difficulty="5")
        self.manager.add_task(self.alias_task)
        self.manager.add_task(second)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIsInstance(tasks[0], self.tasks_task_cls)
        self.assertEqual(tasks[0].name, "Alias task")
        self.assertEqual(tasks[1].duration, 25)
        self.assertTrue(self.manager.remove_task("Alias task"))
        self.assertEqual(len(self.manager.list_tasks()), 1)


if __name__ == "__main__":
    unittest.main()
