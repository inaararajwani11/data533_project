from __future__ import annotations

from datetime import date
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.focus_session import FocusSession


def total_distractions(sessions: List[FocusSession]) -> int:
    return sum(s.distractions for s in sessions)


def distraction_rate_per_hour(
    sessions: List[FocusSession],
) -> Optional[float]:
    total_minutes = 0
    total = 0

    for s in sessions:
        duration = s.duration_minutes()
        if duration is not None and duration > 0:
            total_minutes += duration
            total += s.distractions

    if total_minutes == 0:
        return None

    hours = total_minutes / 60.0
    return total / hours


def distractions_by_day(
    sessions: List[FocusSession],
) -> Dict[date, int]:
    
    result: Dict[date, int] = {}

    for s in sessions:
        day = s.start_time.date()
        result[day] = result.get(day, 0) + s.distractions

    return result


def distraction_rate_by_task(
    sessions: List[FocusSession],
) -> Dict[str, float]:
   
    total_minutes_by_label: Dict[str, int] = {}
    total_distractions_by_label: Dict[str, int] = {}

    for s in sessions:
        # Derive a label
        if getattr(s, "task", None) is not None:
            label = getattr(s.task, "name", "Task")
        elif getattr(s, "habit", None) is not None:
            label = f"Habit: {getattr(s.habit, 'name', 'Habit')}"
        else:
            label = s.label

        duration = s.duration_minutes()
        if duration is None or duration <= 0:
            continue

        total_minutes_by_label[label] = total_minutes_by_label.get(label, 0) + duration
        total_distractions_by_label[label] = (
            total_distractions_by_label.get(label, 0) + s.distractions
        )

    rates: Dict[str, float] = {}
    for label, minutes in total_minutes_by_label.items():
        hours = minutes / 60.0
        if hours <= 0:
            continue
        total = total_distractions_by_label.get(label, 0)
        rates[label] = total / hours

    return rates