import unittest
from datetime import date, timedelta
from unittest.mock import patch

from core.habit import Habit, HabitManager


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


if __name__ == "__main__":
    unittest.main()
