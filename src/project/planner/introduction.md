# Planner subpackage overview

Turns `Task` objects into time-blocked daily schedules using priority scoring and interchangeable scheduling strategies. Provides planners, priority strategies, and schedulers behind a simple `generate_daily_plan` entrypoint.

## Modules
- `base_planner.py`: `PlannedBlock`; abstract `Planner` with `_filter_active_tasks` / `_sort_tasks`; concrete planners (`StudyPlanner`, `EnergyPlanner`, `BalancedPlanner`).
- `priority_strategy.py`: scoring strategies (`SimplePriority`, `DeadlinePriority`, `EnergyAwarePriority`) blending urgency, importance, difficulty, duration, and energy matching.
- `schedulers.py`: abstract `Scheduler`; `SequentialScheduler` (back-to-back blocks) and `PomodoroScheduler` (25/5 splits).
- `daily_plan.py`: user-facing `get_planner` / `generate_daily_plan`, HH:MM validation, energy-level clamping, planner exceptions (`PlannerConfigurationError`, `SchedulingWindowError`).

## Features
- Modes: study (deadline-aware), energy-aware, balanced (recovery interleave).
- Pluggable scheduling: sequential vs. Pomodoro.
- Input safety: time parsing, energy clamping, filtering completed/zero-duration tasks.
- Clear exceptions for misconfiguration or invalid windows.

## Integration
- Operates on `core.Task` and returns `PlannedBlock`.
- Swappable strategies/schedulers; extend without changing callers.
- Used by demos (`run_demo.py`, `test_code.py`) via `generate_daily_plan`.

## Tests & coverage
- Planner suites: `tests/test_planner.py`, `tests/test_planner_helpers.py`.
- Run planner-only:
  ```bash
  $env:PYTHONPATH="src\project"
  python -m unittest -v tests.test_planner tests.test_planner_helpers
  ```
- Full suite with coverage:
  ```bash
  $env:PYTHONPATH="src\project"
  python -m coverage run -m unittest discover -s tests -t .
  python -m coverage report
  ```
