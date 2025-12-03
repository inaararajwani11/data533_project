The planner subpackage turns Task objects into time-blocked schedules using priority scoring and scheduling strategies. It provides the planner abstractions, concrete planner variants, and helper functions that select the right strategy for a given day.

- `base_planner.py`: defines the `PlannedBlock` dataclass, the abstract `Planner` base, and concrete planners (`StudyPlanner`, `EnergyPlanner`, `BalancedPlanner`).
- `priority_strategy.py`: scoring rules such as `SimplePriority`, `DeadlinePriority`, and `EnergyAwarePriority` that rank tasks before scheduling.
- `schedulers.py`: scheduling algorithms (`SequentialScheduler`, `PomodoroScheduler`) that place tasks within the day’s start/end window.
- `daily_plan.py`: user-facing helpers to pick a planner mode and call `generate_daily_plan` for a full schedule.
