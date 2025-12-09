import unittest
from datetime import date, timedelta

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


if __name__ == "__main__":
    unittest.main()
