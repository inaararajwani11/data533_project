## Core subpackage overview

Models, state, and lifecycle helpers for tasks, habits, and focus sessions. Includes defensive normalization and domain-specific exceptions.

### Modules
- `tasks.py` / `task.py`: `Task` dataclass (normalizes duration/priority/difficulty, planned distractions, pomodoro flag) and `TaskManager` (add/list/remove/next). `task.py` re-exports `Task`/`TaskManager`.
- `habit.py`: `Habit` with streaks, completion dates, due logic; `HabitManager`; CLI helpers (`add_habit_from_input`, `choose_habit`, `show_habit_menu`). Invalid inputs are clamped or defaulted; unrecoverable date issues raise `HabitError`.
- `focus_session.py`: `FocusSession` for task/habit/custom sessions; note-taking, distraction tracking, focus ratings; helpers `start_task_session`, `start_habit_session`, `start_custom_session`. Invalid lifecycle states raise `InvalidSessionError`.
- `exceptions.py`: core-specific exceptions (`InvalidSessionError`, `HabitError`).
- `__init__.py`: package marker.

### Usage example
```python
from core.task import Task, TaskManager
from core.focus_session import start_task_session

task = Task("Read", duration=30, category="study", pomodoro=True)
manager = TaskManager()
manager.add_task(task)
session = start_task_session(task)
session.record_distraction()
session.end_session()
print(session.summary())
```

### Testing & coverage (repo root)
```bash
$env:PYTHONPATH="src\project"
python -m unittest -v tests.test_core
python -m coverage run -m unittest discover -s tests -t .
python -m coverage report
```

### Notes
- Numeric fields are normalized and clamped to sensible ranges.
- Completed tasks are filtered out by planners and demos.
- Habit/session guards raise domain errors instead of failing silently.
