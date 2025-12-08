import unittest
from datetime import datetime, timedelta

from core.task import Task
from planner.daily_plan import generate_daily_plan, get_planner
from planner.schedulers import SequentialScheduler


class PlannerTests(unittest.TestCase):
    def test_get_planner_invalid_mode(self):
        with self.assertRaises(ValueError):
            get_planner("unknown")

    def test_generate_daily_plan_requires_valid_window(self):
        tasks = [Task("Study", 30, category="study")]
        with self.assertRaises(ValueError):
            generate_daily_plan(tasks, start="10:00", end="09:00")

    def test_generate_daily_plan_rejects_bad_time_format(self):
        tasks = [Task("Study", 30, category="study")]
        with self.assertRaisesRegex(ValueError, "HH:MM"):
            generate_daily_plan(tasks, start="9am", end="10:00")

    def test_generate_skips_completed_and_zero_duration(self):
        tasks = [
            Task("Done", 20, category="study", completed=True),
            Task("Zero", 0, category="study"),
            Task("Todo", 30, category="study"),
        ]
        blocks = generate_daily_plan(tasks, start="09:00", end="10:00")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].task.name, "Todo")

    def test_pomodoro_scheduler_splits_blocks(self):
        tasks = [Task("Pomodoro Task", 50, category="study", pomodoro=True)]
        blocks = generate_daily_plan(tasks, start="09:00", end="10:00")
        self.assertEqual(len(blocks), 2)
        self.assertEqual((blocks[0].end - blocks[0].start), timedelta(minutes=25))
        self.assertEqual((blocks[1].end - blocks[1].start), timedelta(minutes=25))
        # Break time should push the second block start 30 minutes after the first start
        self.assertEqual((blocks[1].start - blocks[0].start), timedelta(minutes=30))

    def test_sequential_scheduler_stops_at_day_end(self):
        scheduler = SequentialScheduler()
        tasks = [
            Task("Short", 30, category="study"),
            Task("Too Long", 45, category="study"),
        ]
        start = datetime(2024, 1, 1, 9, 0)
        end = datetime(2024, 1, 1, 9, 50)

        blocks = scheduler.schedule(tasks, start, end)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].task.name, "Short")

    def test_balanced_planner_interleaves_recovery(self):
        tasks = [
            Task("Study 1", 10, category="study"),
            Task("Study 2", 10, category="study"),
            Task("Break", 5, category="recovery"),
            Task("Study 3", 10, category="study"),
        ]

        blocks = generate_daily_plan(tasks, mode="balanced", start="09:00", end="10:00")
        self.assertGreaterEqual(len(blocks), 3)
        names = [b.task.name for b in blocks[:3]]
        self.assertEqual(names, ["Study 1", "Study 2", "Break"])
        self.assertEqual(blocks[2].task.category, "recovery")

    def test_energy_planner_prefers_easier_task_when_low_energy(self):
        tasks = [
            Task("Hard Task", 40, category="study", difficulty=5),
            Task("Easy Task", 20, category="study", difficulty=1),
        ]

        blocks = generate_daily_plan(
            tasks, mode="energy", energy_level=1, start="09:00", end="10:30"
        )
        self.assertGreaterEqual(len(blocks), 2)
        self.assertEqual(blocks[0].task.name, "Easy Task")

    def test_energy_planner_coerces_string_energy_level(self):
        tasks = [
            Task("Hard Task", 40, category="study", difficulty=5),
            Task("Easy Task", 20, category="study", difficulty=1),
        ]

        blocks = generate_daily_plan(
            tasks, mode="energy", energy_level="1", start="09:00", end="10:30"
        )
        self.assertGreaterEqual(len(blocks), 2)
        self.assertEqual(blocks[0].task.name, "Easy Task")

    def test_energy_planner_clamps_high_energy_level(self):
        tasks = [
            Task("Hard Task", 40, category="study", difficulty=5),
            Task("Easy Task", 20, category="study", difficulty=1),
        ]

        blocks = generate_daily_plan(
            tasks, mode="energy", energy_level=10, start="09:00", end="10:30"
        )
        self.assertGreaterEqual(len(blocks), 2)
        self.assertEqual(blocks[0].task.name, "Hard Task")

    def test_study_planner_prioritizes_deadline(self):
        today = datetime.now().date()
        tasks = [
            Task("Due Tomorrow", 20, category="study", deadline=today + timedelta(days=1)),
            Task("Due Today", 20, category="study", deadline=today),
        ]

        blocks = generate_daily_plan(tasks, mode="study", start="09:00", end="10:00")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].task.name, "Due Today")

    def test_overdue_tasks_get_prioritized_first(self):
        today = datetime.now().date()
        tasks = [
            Task("Overdue", 20, category="study", deadline=today - timedelta(days=1)),
            Task("Due Today", 20, category="study", deadline=today),
        ]

        blocks = generate_daily_plan(tasks, mode="study", start="09:00", end="10:00")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].task.name, "Overdue")


if __name__ == "__main__":
    unittest.main()
