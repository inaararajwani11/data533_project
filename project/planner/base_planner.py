

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Sequence
from abc import ABC, abstractmethod

from core.task import Task
from planner.priority_strategy import PriorityStrategy, DeadlinePriority, EnergyAwarePriority
from planner.schedulers import Scheduler, SequentialScheduler


# -------------------------------------------------------------------
# Data structure for planned time blocks
# -------------------------------------------------------------------


@dataclass
class PlannedBlock:
    
    task: Task
    start: datetime
    end: datetime

    def __str__(self) -> str:
        start_str = self.start.strftime("%H:%M")
        end_str = self.end.strftime("%H:%M")
        return f"{start_str}–{end_str}  {self.task.name}"




class Planner(ABC):


    def __init__(self, priority_strategy: PriorityStrategy, scheduler: Scheduler) -> None:
        self.priority_strategy = priority_strategy
        self.scheduler = scheduler

    def _sort_tasks(self, tasks: Sequence[Task]) -> List[Task]:
       
        return sorted(
            tasks,
            key=self.priority_strategy.score,
            reverse=True,
        )

    @abstractmethod
    def generate(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List[PlannedBlock]:
        raise NotImplementedError



class StudyPlanner(Planner):

    def __init__(self, scheduler: Scheduler | None = None) -> None:
        priority = DeadlinePriority()
        if scheduler is None:
            scheduler = SequentialScheduler()
        super().__init__(priority_strategy=priority, scheduler=scheduler)

    def generate(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List[PlannedBlock]:
        # Sort by deadline/difficulty/etc. (handled inside DeadlinePriority)
        sorted_tasks = self._sort_tasks(tasks)
        # Delegate to the chosen scheduler to place tasks into time blocks
        return self.scheduler.schedule(sorted_tasks, day_start, day_end)


class EnergyPlanner(Planner):


    def __init__(
        self,
        energy_level: int,
        scheduler: Scheduler | None = None,
    ) -> None:
       
        priority = EnergyAwarePriority(energy_level=energy_level)
        if scheduler is None:
            scheduler = SequentialScheduler()
        super().__init__(priority_strategy=priority, scheduler=scheduler)

    def generate(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List[PlannedBlock]:
        sorted_tasks = self._sort_tasks(tasks)
        return self.scheduler.schedule(sorted_tasks, day_start, day_end)


class BalancedPlanner(Planner):
 

    def __init__(
        self,
        priority_strategy: PriorityStrategy | None = None,
        scheduler: Scheduler | None = None,
    ) -> None:
        # Default: use DeadlinePriority + SequentialScheduler
        if priority_strategy is None:
            priority_strategy = DeadlinePriority()
        if scheduler is None:
            scheduler = SequentialScheduler()
        super().__init__(priority_strategy=priority_strategy, scheduler=scheduler)

    def generate(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List[PlannedBlock]:
        # Simple balancing rule:
        #   - Treat "recovery" category tasks as micro-breaks.
        #   - Other tasks get sorted by normal priority.
        recovery_tasks: List[Task] = []
        regular_tasks: List[Task] = []

        for t in tasks:
            if getattr(t, "category", None) == "recovery":
                recovery_tasks.append(t)
            else:
                regular_tasks.append(t)

        # Sort regular tasks by priority
        regular_sorted = self._sort_tasks(regular_tasks)

        # Heuristic: interleave one recovery task after every N regular tasks
        N = 2
        combined: List[Task] = []
        idx_recovery = 0

        for i, task in enumerate(regular_sorted):
            combined.append(task)
            # After every N tasks, if a recovery task is available, insert it
            if (i + 1) % N == 0 and idx_recovery < len(recovery_tasks):
                combined.append(recovery_tasks[idx_recovery])
                idx_recovery += 1

        # Any remaining recovery tasks go at the end
        combined.extend(recovery_tasks[idx_recovery:])

        # Delegate to scheduler
        return self.scheduler.schedule(combined, day_start, day_end)
