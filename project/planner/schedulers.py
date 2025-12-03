"""
schedulers.py

Defines how tasks are placed into time blocks.

This module provides:
- Scheduler (abstract base class)
- SequentialScheduler
- PomodoroScheduler (optional example)

Schedulers are used by Planner subclasses to convert an ordered
list of tasks into concrete start/end times (PlannedBlock objects).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Sequence

from core.task import Task

# NOTE: We import PlannedBlock lazily inside methods to avoid circular imports
# with base_planner.py (which also imports Scheduler).


class Scheduler(ABC):
    """
    Abstract base class for all schedulers.

    A scheduler receives:
    - an ordered list of tasks
    - a planning window [day_start, day_end]

    and returns a list of PlannedBlock objects.
    """

    @abstractmethod
    def schedule(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List["PlannedBlock"]:
        """
        Build a schedule of time blocks for the given tasks.

        Returns a list of PlannedBlock objects.
        """
        raise NotImplementedError


class SequentialScheduler(Scheduler):
    """
    Simple scheduler that fills the day sequentially:

    - Takes tasks in the given order.
    - Assigns each task a block of time equal to its duration.
    - Stops when there is no remaining time in the day.
    """

    def schedule(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List["PlannedBlock"]:
        from planner.base_planner import PlannedBlock  # lazy import

        blocks: List[PlannedBlock] = []
        current_start = day_start

        for task in tasks:
            duration_minutes = getattr(task, "duration", 0) or 0
            if duration_minutes <= 0:
                continue  # skip zero-length tasks

            block_duration = timedelta(minutes=duration_minutes)
            block_end = current_start + block_duration

            if block_end > day_end:
                # No more room in the schedule
                break

            blocks.append(PlannedBlock(task=task, start=current_start, end=block_end))
            current_start = block_end

        return blocks


class PomodoroScheduler(Scheduler):
    """
    Scheduler that uses a simple Pomodoro-like pattern:

    - Work blocks of `work_minutes` length.
    - Short break between blocks.
    - Tasks are split across multiple work blocks if needed.
    """

    def __init__(
        self,
        work_minutes: int = 25,
        break_minutes: int = 5,
    ) -> None:
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes

    def schedule(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List["PlannedBlock"]:
        from planner.base_planner import PlannedBlock  # lazy import

        blocks: List[PlannedBlock] = []
        current_start = day_start

        work_delta = timedelta(minutes=self.work_minutes)
        break_delta = timedelta(minutes=self.break_minutes)

        for task in tasks:
            remaining_minutes = getattr(task, "duration", 0) or 0
            if remaining_minutes <= 0:
                continue

            while remaining_minutes > 0:
                block_end = current_start + work_delta
                if block_end > day_end:
                    return blocks  # no more space

                # Create a work block
                blocks.append(
                    PlannedBlock(task=task, start=current_start, end=block_end)
                )

                remaining_minutes -= self.work_minutes
                current_start = block_end

                # Add break after each pomodoro if there's still task time left
                if remaining_minutes > 0:
                    break_end = current_start + break_delta
                    if break_end > day_end:
                        return blocks
                    # Breaks are not tied to a task; you could also represent them
                    # with a special "break" Task if you want.
                    current_start = break_end

        return blocks
