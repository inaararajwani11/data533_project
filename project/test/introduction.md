The test subpackage verifies the core models and planner flows with pytest to ensure scheduling and tracking work as expected.

- `conftest.py`: adds the repository root to `sys.path` so tests can import project modules directly.
- `test_core.py`: exercises tasks, habits, and focus sessions, including creation, listing, distractions, ratings, and session durations.
- `test_tasks.py`: covers basic task creation and TaskManager add/list behavior.
- `test_planner.py`: drives the planners end-to-end:
  * invalid modes and time windows raise errors
  * HH:MM strings are validated
  * completed/zero-duration tasks are skipped
  * pomodoro tasks split into 25/5 blocks
  * balanced mode interleaves recovery tasks
  * sequential scheduler stops at day end
  * energy levels are parsed/clamped (strings and out-of-range values)
  * deadlines prioritize overdue/today before tomorrow

Run `pytest` from the project root to execute the full suite.
