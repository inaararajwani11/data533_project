# Subpackage: `planner`

**Purpose:**
Turn `Task` objects into time-blocked daily schedules using priority scoring and scheduling strategies.

**This subpackage provides:**
- A clear scheduling responsibility with interchangeable planners/schedulers
- Four modules (planner core, priorities, schedulers, user-facing helpers)
- OOP classes plus utility functions with defined inputs/outputs
- Optional Pomodoro-aware scheduling hook

---

## Modules Inside This Subpackage

### Module 1: `base_planner.py`
**Contains:**
- `PlannedBlock` dataclass for scheduled blocks
- Abstract `Planner` base class (inheritance) with `_filter_active_tasks` and `_sort_tasks`
- Concrete planners: `StudyPlanner`, `EnergyPlanner`, `BalancedPlanner`
- Uses priority strategies to order tasks before scheduling

---

### Module 2: `priority_strategy.py`
**Contains:**
- Priority strategies to rank tasks (`SimplePriority`, `DeadlinePriority`, `EnergyAwarePriority`)
- Scoring blends deadline urgency, category importance, duration penalty, and energy matching
- Protocol-style typing for deadline/difficulty awareness

---

### Module 3: `schedulers.py`
**Contains:**
- Abstract `Scheduler` base (inheritance) for scheduling implementations
- `SequentialScheduler` to lay tasks back-to-back within a start/end window
- `PomodoroScheduler` to split tasks into 25/5 style focus/break blocks

---

### Module 4: `daily_plan.py`
**Contains:**
- User-facing helpers `get_planner` and `generate_daily_plan`
- Input validation for planner mode, energy level (clamped 1-5), and HH:MM start/end
- Optional Pomodoro preference that switches scheduler automatically

---

## Key Features of This Subpackage

This subpackage provides:

- Mode selection: study, energy-aware, or balanced (with recovery task interleave)
- Priority scoring that respects deadlines, difficulty, and category importance
- Scheduling engines: sequential and Pomodoro
- Safe input handling (time parsing, energy-level clamping) before scheduling
- Simple entrypoint (`generate_daily_plan`) for CLI or other callers

---

## Integration With Main System

This subpackage:

- Is imported by higher-level code (e.g., demos/CLI) via `generate_daily_plan`
- Operates on `core.Task` objects and returns `PlannedBlock` instances
- Keeps planners/schedulers swappable to stay modular and extensible
- Can be extended with new priority strategies or scheduling algorithms without touching callers

---

## Summary

The `planner` subpackage is responsible for:

- Turning tasks into daily schedules via pluggable planners and schedulers
- Clear module boundaries (core planners, priorities, schedulers, user helpers)
- Inheritance-based extensibility with well-defined inputs/outputs
- Reusable, testable scheduling components ready for CLI or API use
