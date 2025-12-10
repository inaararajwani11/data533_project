"""
Custom test suite to explicitly collect planner and core module tests.
Run with: python -m unittest test.test_suite
"""

import unittest

from .test_planner import PlannerTests
from .test_planner_helpers import PlannerHelperTests
from .test_focuscore import TestFocusCore
from .test_core import (
    TestFocusSessionModule,
    TestHabitModule,
    TestTaskAliasModule,
    TestTasksModule,
)


def suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for case in (
        PlannerTests,
        PlannerHelperTests,
        TestFocusCore,
        TestTasksModule,
        TestHabitModule,
        TestFocusSessionModule,
        TestTaskAliasModule,
    ):
        suite.addTests(loader.loadTestsFromTestCase(case))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    if not result.wasSuccessful():
        raise SystemExit(1)
