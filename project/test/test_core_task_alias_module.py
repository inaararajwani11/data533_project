import unittest

import core.task as task_module
from core.task import Task as AliasTask, TaskManager as AliasTaskManager
from core.tasks import Task as TasksTask, TaskManager as TasksTaskManager


class TestTaskAliasModule(unittest.TestCase):
    """Tests for the lightweight core.task re-export module."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks_task_cls = TasksTask
        cls.tasks_manager_cls = TasksTaskManager

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
