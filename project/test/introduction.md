The test subpackage verifies the core models and planner flows with pytest to ensure scheduling and tracking work as expected.

- `conftest.py`: adds the repository root to `sys.path` so tests can import project modules directly.
- `test_core.py`: exercises tasks, habits, and focus sessions, including creation, listing, distractions, ratings, and session durations.
- `test_tasks.py`: covers basic task creation and TaskManager add/list behavior.
- `test_planner.py`: checks Study, Energy, and Balanced planners to confirm they generate time blocks and respect recovery and energy rules.

Run `pytest` from the project root to execute the full suite.
