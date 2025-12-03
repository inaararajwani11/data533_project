"""
priority_strategy.py

Defines how task priority scores are computed.

This module provides:
- PriorityStrategy (abstract base class)
- SimplePriority
- DeadlinePriority
- EnergyAwarePriority

These are used by Planner classes in base_planner.py to sort tasks
before scheduling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol

from core.task import Task


class SupportsDeadline(Protocol):
    deadline: date | None


class SupportsDifficulty(Protocol):
    difficulty: int | None


class PriorityStrategy(ABC):
    """
    Abstract base class for all priority scoring strategies.

    Subclasses must implement score(task), returning a numeric
    priority score: higher means more important/urgent.
    """

    @abstractmethod
    def score(self, task: Task) -> float:
        """
        Compute a priority score for a given task.

        Parameters
        ----------
        task : Task
            The task to score.

        Returns
        -------
        float
            Higher values indicate higher priority.
        """
        raise NotImplementedError


class SimplePriority(PriorityStrategy):
    """
    Very simple priority: combines duration and (optional) priority attribute.

    Intended as a baseline or fallback strategy.
    """

    def score(self, task: Task) -> float:
        duration = getattr(task, "duration", 0) or 0  # minutes
        base_priority = getattr(task, "priority", 1) or 1

        # Shorter tasks get slightly higher score (less penalty)
        duration_hours = duration / 60
        duration_penalty = 0.2 * duration_hours

        return float(base_priority) - duration_penalty


class DeadlinePriority(PriorityStrategy):
    """
    Priority strategy that emphasizes deadlines and difficulty.

    Heuristic:
    - Urgency grows as the deadline approaches.
    - More difficult and more important categories get extra weight.
    """

    def score(self, task: Task) -> float:
        today = date.today()

        # 1) Urgency based on time until deadline
        deadline = getattr(task, "deadline", None)
        if deadline is not None:
            days_left = (deadline - today).days
            urgency = 1.0 / max(days_left, 1)  # 1.0 if due today, 0.5 if tomorrow, etc.
        else:
            urgency = 0.0

        # 2) Difficulty (default 3 on a 1–5 scale)
        difficulty = getattr(task, "difficulty", 3) or 3

        # 3) Importance from category
        category = getattr(task, "category", None)
        category_weights = {
            "study": 3.0,
            "admin": 1.0,
            "recovery": 2.0,
            "other": 1.0,
            None: 1.0,
        }
        importance = category_weights.get(category, 1.0)

        # 4) Duration penalty (long tasks are slightly harder to fit)
        duration = getattr(task, "duration", 0) or 0
        duration_hours = duration / 60.0
        duration_penalty = 0.3 * duration_hours

        score = (
            4.0 * urgency
            + 3.0 * importance
            + 2.0 * difficulty
            - duration_penalty
        )

        # Optional bump if the task is explicitly marked as must-do-today
        if getattr(task, "must_do_today", False):
            score += 10.0

        return float(score)


class EnergyAwarePriority(PriorityStrategy):
    """
    Priority strategy that tries to match task difficulty with the
    user's current energy level.

    Idea:
        - If difficulty ~ energy level, score is high.
        - If difficulty >> energy or << energy, score drops.
    """

    def __init__(self, energy_level: int = 3) -> None:
        self.energy_level = max(1, min(5, energy_level))

    def score(self, task: Task) -> float:
        difficulty = getattr(task, "difficulty", 3) or 3
        difficulty = max(1, min(5, int(difficulty)))

        # Compatibility: smaller difference -> better match
        diff = abs(difficulty - self.energy_level)
        compatibility = max(0.0, 5.0 - diff)  # 0 to 5

        # Slight emphasis on tasks with deadlines
        today = date.today()
        deadline = getattr(task, "deadline", None)
        if deadline is not None:
            days_left = (deadline - today).days
            urgency = 1.0 / max(days_left, 1)
        else:
            urgency = 0.0

        # Combine compatibility and urgency
        score = 2.5 * compatibility + 3.0 * urgency

        return float(score)
