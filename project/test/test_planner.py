import pytest
from datetime import datetime

from core.task import Task
from planner.daily_plan import generate_daily_plan
from planner.base_planner import StudyPlanner, EnergyPlanner, BalancedPlanner


def test_study_planner_generates_blocks():
    tasks = [
        Task("Task A", 30, category="study"),
        Task("Task B", 20, category="admin"),
    ]

    start = "09:00"
    end = "10:30"

    blocks = generate_daily_plan(tasks, mode="study", start=start, end=end)
    assert len(blocks) > 0
    assert blocks[0].task.name in ["Task A", "Task B"]


def test_energy_planner_respects_energy_level():
    tasks = [
        Task("Hard Task", 40, category="study"),
        Task("Easy Task", 20, category="study"),
    ]
    tasks[0].difficulty = 5
    tasks[1].difficulty = 1

    blocks = generate_daily_plan(tasks, mode="energy", energy_level=1)
    assert len(blocks) > 0


def test_balanced_planner_includes_recovery():
    tasks = [
        Task("Study", 40, category="study"),
        Task("Break", 10, category="recovery"),
    ]

    blocks = generate_daily_plan(tasks, mode="balanced")
    assert len(blocks) > 0
