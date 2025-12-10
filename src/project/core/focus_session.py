"""
focus_session.py

Monitor deep‑work sessions, focus quality, and distractions.

Key class
---------
- FocusSession: represents one focused work block on a task, habit,
  or custom label.

Convenience functions
---------------------
- start_task_session()
- start_habit_session()
- start_custom_session()
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from .tasks import Task
from .habit import Habit



class FocusSession:
    """
    Simple timer for one focus period.

    A session can be tied to:
      - a Task
      - a Habit
      - or just a custom text label

    Attributes
    ----------
    task : Task | None
    habit : Habit | None
    label : str
    start_time : datetime
    end_time : datetime | None
    distractions : int
    focus_rating : int | None   (1–5)
    notes : list[str]
    """

    def __init__(
        self,
        task: Optional[Task] = None,
        habit: Optional[Habit] = None,
        label: Optional[str] = None,
        auto_checkin_habit: bool = False,
    ) -> None:
        if task is not None and habit is not None:
            raise ValueError("A session can be for a task OR a habit, not both.")

        self.task = task
        self.habit = habit
        self.auto_checkin_habit = auto_checkin_habit

        if label is not None:
            self.label = label
        elif task is not None:
            self.label = task.name
        elif habit is not None:
            self.label = habit.name
        else:
            self.label = "Focus session"

        self.kind = "task" if task else ("habit" if habit else "custom")
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None

        self.distractions: int = 0
        self.focus_rating: Optional[int] = None
        self.notes: List[str] = []

    # -------------------- Methods (from slide) --------------------

    def end_session(self, checkin_habit: Optional[bool] = None) -> None:
        """
        Mark the session as finished.

        If this is a habit session and `checkin_habit` is True (or
        auto_checkin_habit is True), mark the habit as completed today.
        """
        if self.end_time is not None:
            return  # already ended

        self.end_time = datetime.now()

        should_checkin = (
            self.auto_checkin_habit if checkin_habit is None else checkin_habit
        )

        if should_checkin and self.habit is not None:
            self.habit.complete_today()

    def record_distraction(self) -> None:
        """Increment the distraction counter by one."""
        self.distractions += 1

    def add_note(self, text: str) -> None:
        """Append a short note or reflection to this session."""
        if text.strip():
            self.notes.append(text.strip())

    def rate_focus(self, rating: int) -> None:
        """
        Set a focus rating on a 1–5 scale.
        Raises ValueError if outside the allowed range.
        """
        if rating < 1 or rating > 5:
            raise ValueError("Focus rating must be between 1 and 5.")
        self.focus_rating = rating

    def duration_minutes(self) -> Optional[int]:
        """
        Return session length in whole minutes once ended.
        Returns None if the session has not ended yet.
        """
        if self.end_time is None:
            return None
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() // 60)

    def summary(self) -> Dict[str, Any]:
        """
        Small dictionary summary that can be printed or stored.
        """
        return {
            "label": self.label,
            "kind": self.kind,
            "start": self.start_time.isoformat(),
            "end": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes(),
            "distractions": self.distractions,
            "rating": self.focus_rating,
            "notes": list(self.notes),
        }

    def __repr__(self) -> str:
        return (
            f"FocusSession(kind={self.kind!r}, label={self.label!r}, "
            f"start={self.start_time!r}, end={self.end_time!r})"
        )


# ---------------- Convenience functions (from slide) ----------------


def start_task_session(task: Task) -> FocusSession:
    """Create and return a focus session tied to a Task."""
    return FocusSession(task=task)


def start_habit_session(habit: Habit, auto_checkin: bool = True) -> FocusSession:
    """
    Create and return a focus session tied to a Habit.

    If auto_checkin is True, the habit will be marked as completed
    when end_session() is called.
    """
    return FocusSession(habit=habit, auto_checkin_habit=auto_checkin)


def start_custom_session(label: str) -> FocusSession:
    """Create and return a focus session with a free-form label."""
    return FocusSession(label=label or "Focus session")
