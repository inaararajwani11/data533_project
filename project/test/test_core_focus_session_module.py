import unittest
from datetime import date, timedelta
from typing import Optional

from core.focus_session import (
    FocusSession,
    start_custom_session,
    start_habit_session,
    start_task_session,
)
from core.habit import Habit
from core.tasks import Task


class TestFocusSessionModule(unittest.TestCase):
    """Tests for the core.focus_session module."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.today = date.today()
        cls.yesterday = cls.today - timedelta(days=1)

    def setUp(self) -> None:
        self.task = Task("Deep work", duration=50)
        self.habit = Habit("Evening stretch", streak=1, last_completed=self.yesterday)
        self.session: Optional[FocusSession] = None

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

        custom = start_custom_session("Review day")
        self.assertEqual(custom.kind, "custom")
        self.assertEqual(custom.label, "Review day")


if __name__ == "__main__":
    unittest.main()
