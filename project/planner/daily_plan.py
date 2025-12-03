"""
daily_plan.py

User-facing interface for generating a daily schedule
using the planners defined in base_planner.py.

This module provides:
- generate_daily_plan(): main function for creating a study plan
- optional CLI mode for quick manual runs

It ties together:
    * a Planner (StudyPlanner, EnergyPlanner, BalancedPlanner)
    * Task list provided by the user
    * start/end time for the planning window
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Sequence

from core.task import Task
from planner.base_planner import (
    Planner,
    StudyPlanner,
    EnergyPlanner,
    BalancedPlanner,
)
from planner.base_planner import PlannedBlock


# -------------------------------------------------------------------
# Planner selection helper
# -------------------------------------------------------------------

def get_planner(
    mode: str = "study",
    energy_level: int = 3,
) -> Planner:
    """
    Return a Planner instance based on the selected mode.

    Parameters
    ----------
    mode : str
        One of: "study", "energy", "balanced".
    energy_level : int
        Used only for EnergyPlanner (1–5).

    Returns
    -------
    Planner
        A configured Planner instance.
    """
    mode = mode.lower()

    if mode == "study":
        return StudyPlanner()

    elif mode == "energy":
        return EnergyPlanner(energy_level=energy_level)

    elif mode == "balanced":
        return BalancedPlanner()

    else:
        raise ValueError(
            f"Unknown planner mode '{mode}'. Use 'study', 'energy', or 'balanced'."
        )


# -------------------------------------------------------------------
# Main daily plan generator
# -------------------------------------------------------------------

def generate_daily_plan(
    tasks: Sequence[Task],
    mode: str = "study",
    energy_level: int = 3,
    start: str = "09:00",
    end: str = "18:00",
) -> List[PlannedBlock]:
    """
    Generate a daily schedule using the specified planner mode.

    Parameters
    ----------
    tasks : sequence of Task
        List of Task objects needing to be scheduled.
    mode : str
        Planner type: "study", "energy", or "balanced".
    energy_level : int
        Only applies when mode="energy".
    start : str
        Start time as HH:MM (24-hour format).
    end : str
        End time as HH:MM (24-hour format).

    Returns
    -------
    list of PlannedBlock
        Scheduled time blocks for the day.
    """

    # Convert HH:MM to datetime objects (using today's date)
    today = datetime.today().date()
    start_dt = datetime.strptime(start, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
    end_dt = datetime.strptime(end, "%H:%M").replace(year=today.year, month=today.month, day=today.day)

    planner = get_planner(mode=mode, energy_level=energy_level)

    return planner.generate(tasks=tasks, day_start=start_dt, day_end=end_dt)


# -------------------------------------------------------------------
# Optional CLI usage (for debugging / local testing)
# -------------------------------------------------------------------

def _demo():
    """
    Simple demo for running the planner manually.
    """

    # Example placeholder tasks
    tasks = [
        Task("Study MDS", duration=90, category="study"),
        Task("Read textbook", duration=45, category="study"),
        Task("Email admin office", duration=20, category="admin"),
        Task("Stretch / break", duration=10, category="recovery"),
    ]

    print("\n=== FocusForge Daily Planner Demo ===")
    mode = input("Choose planner mode (study / balanced / energy): ").strip().lower()

    if mode == "energy":
        level = int(input("Energy level (1–5): ").strip())
    else:
        level = 3

    blocks = generate_daily_plan(tasks, mode=mode, energy_level=level)

    print("\nGenerated Plan:")
    for block in blocks:
        print(" ", block)


# Allow running file directly
if __name__ == "__main__":
    _demo()
