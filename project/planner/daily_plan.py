
from __future__ import annotations

from datetime import datetime
import sys
from pathlib import Path
from typing import List, Sequence

# Allow running this module directly by adding repo root to sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.task import Task
from planner.base_planner import (
    Planner,
    StudyPlanner,
    EnergyPlanner,
    BalancedPlanner,
)
from planner.base_planner import PlannedBlock


def get_planner(
    mode: str = "study",
    energy_level: int = 3,
) -> Planner:

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


def generate_daily_plan(
    tasks: Sequence[Task],
    mode: str = "study",
    energy_level: int = 3,
    start: str = "09:00",
    end: str = "18:00",
) -> List[PlannedBlock]:


    today = datetime.today().date()
    start_dt = datetime.strptime(start, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
    end_dt = datetime.strptime(end, "%H:%M").replace(year=today.year, month=today.month, day=today.day)

    planner = get_planner(mode=mode, energy_level=energy_level)

    return planner.generate(tasks=tasks, day_start=start_dt, day_end=end_dt)



def _demo():

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
