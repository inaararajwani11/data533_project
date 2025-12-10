## FocusPro Package (Overview & Usage)

An educational productivity toolkit showing tasks, habits, planning, focus sessions, and analytics. Three sub-packages (`core`, `planner`, `analytics`) plus an interactive demo (`run_demo.py`).

### Directory structure
- `core/` (models + state)
  - `tasks.py` / `task.py`: Task dataclass, TaskManager (add/list/remove/next), planned distractions, completion flag, pomodoro flag.
  - `habit.py`: Habit model + HabitManager; check-in, streaks, interactive helpers.
  - `focus_session.py`: FocusSession (task/habit/custom), distraction tracking, focus rating; helpers `start_task_session`, `start_habit_session`, `start_custom_session`.
- `planner/` (scheduling logic)
  - `base_planner.py`: Inheritance/ABC layer (`Planner` abstract base), concrete planners `StudyPlanner`, `EnergyPlanner`, `BalancedPlanner`, and `PlannedBlock` dataclass.
  - `priority_strategy.py`: Scoring strategies (`DeadlinePriority`, `EnergyAwarePriority`).
  - `schedulers.py`: Scheduling algorithms (`SequentialScheduler`, `PomodoroScheduler`) implementing `Scheduler` ABC.
  - `daily_plan.py`: User-facing `generate_daily_plan` and planner selector.
- `analytics/` (reports + scoring)
  - `distraction.py`: Distraction rates overall/by task.
  - `focuscore.py`: Weekly focus score + grade.
  - `weekly_report.py`: Weekly summary aggregator + text formatter.
- `run_demo.py`: Interactive demo that wires all pieces together.
- `tasks.json` / `habits.json` (optional data inputs).
- `test/`: Pytest coverage for tasks, planner, and core wiring.

### Planner function reference (no code, inputs/outputs)

`planner/daily_plan.py`

| Function | Inputs | Output | Notes |
| --- | --- | --- | --- |
| `get_planner(mode="study", energy_level=3)` | `mode` (`study` \| `energy` \| `balanced`), `energy_level` (int 1-5) | `Planner` instance | Selects appropriate planner subclass. |
| `generate_daily_plan(tasks, mode="study", energy_level=3, start="09:00", end="18:00")` | `tasks` (sequence of `Task`), planner options, `start`/`end` (HH:MM) | `List[PlannedBlock]` | Builds a daily schedule using chosen planner/scheduler. |
| `_demo()` | none (uses sample tasks, CLI prompts) | `None` | Simple interactive demo of planner only. |

`planner/base_planner.py`

| Class/Method | Inputs | Output | Notes |
| --- | --- | --- | --- |
| `PlannedBlock.__str__()` | self | `str` | Formats a planned block as `HH:MM–HH:MM  task`. |
| `Planner._sort_tasks(tasks)` | `Sequence[Task]` | `List[Task]` | Orders tasks by current priority strategy. |
| `StudyPlanner.generate(...)` | `tasks`, `day_start`, `day_end` | `List[PlannedBlock]` | Deadline-aware ordering, sequential scheduling. |
| `EnergyPlanner.generate(...)` | `tasks`, `day_start`, `day_end` | `List[PlannedBlock]` | Energy-aware ordering, sequential scheduling. |
| `BalancedPlanner.generate(...)` | `tasks`, `day_start`, `day_end` | `List[PlannedBlock]` | Interleaves recovery tasks, then schedules sequentially. |

`planner/priority_strategy.py`

| Function/Method | Inputs | Output | Notes |
| --- | --- | --- | --- |
| `SimplePriority.score(task)` | `Task` | `float` | Combines base priority and duration penalty. |
| `DeadlinePriority.score(task)` | `Task` | `float` | Weights deadline urgency, difficulty, category importance. |
| `EnergyAwarePriority.score(task)` | `Task` | `float` | Matches task difficulty to user energy and deadline urgency. |

`planner/schedulers.py`

| Function/Method | Inputs | Output | Notes |
| --- | --- | --- | --- |
| `SequentialScheduler.schedule(tasks, day_start, day_end)` | ordered `tasks`, window start/end | `List[PlannedBlock]` | Fills the day in order; stops when out of time. |
| `PomodoroScheduler.schedule(tasks, day_start, day_end)` | ordered `tasks`, window start/end | `List[PlannedBlock]` | Splits tasks into Pomodoro blocks with short breaks. |

### Planner quick start
```python
from planner.daily_plan import generate_daily_plan
from core.task import Task

tasks = [
    Task("Study", 40, category="study"),
    Task("Break", 10, category="recovery"),
]
plan = generate_daily_plan(tasks, mode="balanced", start="09:00", end="10:30")
for block in plan:
    print(block)  # => HH:MM-HH:MM  Task Name
```
`generate_daily_plan` returns a list of `PlannedBlock` objects you can print or inspect.

### Planner tests and exceptions
- Planner uses custom exceptions for configuration and scheduling errors (`PlannerConfigurationError`, `SchedulingWindowError`) and is covered by `tests/test_planner.py` and `tests/test_planner_helpers.py`.
- Run planner tests only:  
  ```bash
  python -m unittest -v tests.test_planner tests.test_planner_helpers
  ```

### CI and coverage (unittest)
- CI runs on GitHub Actions with `coverage run -m unittest discover -s tests -t .`.
- Local run (PowerShell):  
  ```bash
  $env:PYTHONPATH="src\project"
  python -m coverage run -m unittest discover -s tests -t .
  python -m coverage report
  ```

### Package expectations mapping
- 3 sub-packages (`core`, `planner`, `analytics`), each with multiple modules and methods.
- Inheritance: `Planner` (ABC) with concrete subclasses; `Scheduler` ABC with concrete schedulers.
- Documentation/demo: this README + interactive `run_demo.py`; tests in `test/`.
- Collaboration: use git history to show contributions per teammate.

### Quick start
1) Python 3.9+ installed.  
2) From repo root:
```bash
python run_demo.py
```

### Demo flow (interactive)
1. Loads `tasks.json`/`habits.json` if present; otherwise asks if you want to add tasks and how many.  
2. For each task: name, duration, category (menu/custom), difficulty, priority, completed?, Pomodoro?, distractions.  
   - Completed tasks are skipped from planning/sessions.  
   - Pomodoro tags the session and defaults planned distractions to 0.  
3. Habits: load from file or optional prompt; default habit is added if none.  
4. Generates a daily plan and focus sessions; you can optionally tweak distraction counts per session.  
5. Prints analytics: focus score + grade, distraction rates (overall/per task), weekly report text.

### Using your own data
Create JSON files in repo root.

`tasks.json`
```json
[
  {"name": "Write report", "duration": 45, "category": "study", "difficulty": 3, "priority": 2, "pomodoro": true, "completed": false},
  {"name": "Email admin", "duration": 20, "category": "admin", "completed": true}
]
```

`habits.json`
```json
[
  {"name": "Hydrate regularly", "frequency": "daily"},
  {"name": "Evening review", "frequency": "daily"}
]
```

### Tests
```bash
pytest
```

### Notes / extensibility
- Persistence is JSON + prompts (educational focus). Swap in a database or API as needed.
- Pomodoro flag currently just sets planned distractions to zero and tags the session; adjust duration/scheduling via `PomodoroScheduler` if desired.
- Planner selection: `generate_daily_plan(tasks, mode="study", start="09:00", end="12:00")` with modes `study|energy|balanced`.
