Core module overview and error handling
- `core/tasks.py`: Task dataclass with normalization; tolerates bad inputs (duration/priority/difficulty default safely) and TaskManager operations handle unexpected task names without crashing. Re-exported via `core/task.py`.
- `core/habit.py`: Habit model with validation/clamping for streak/frequency and safe handling of invalid `last_completed`; HabitManager and CLI helpers catch input errors; `HabitError` raised for unrecoverable date failures.
- `core/focus_session.py`: FocusSession timer for task/habit/custom labels; explicit `start_session` validation and guarded `end_session`/`duration_minutes` raise `InvalidSessionError` for invalid states.
- `core/exceptions.py`: Custom exceptions `InvalidSessionError` and `HabitError`.
- `core/__init__.py`: Package marker.

Testing (run from repo root)
```bash
$env:PYTHONPATH="."
python -m unittest -v test.test_core
python -m coverage run -m unittest discover -s test -t .
python -m coverage report
```
