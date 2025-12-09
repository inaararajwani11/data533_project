import sys
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from test_core_focus_session_module import TestFocusSessionModule
from test_core_habit_module import TestHabitModule
from test_core_task_alias_module import TestTaskAliasModule
from test_core_tasks_module import TestTasksModule


def suite() -> unittest.TestSuite:
    """Collect core test classes into a single suite."""
    loader = unittest.TestLoader()
    collected = unittest.TestSuite()
    for case in (
        TestTasksModule,
        TestHabitModule,
        TestFocusSessionModule,
        TestTaskAliasModule,
    ):
        collected.addTests(loader.loadTestsFromTestCase(case))
    return collected


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
