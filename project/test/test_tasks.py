import pytest
from core.task import Task, TaskManager


def test_task_creation():
    t = Task(name="Study MDS", duration=60, category="study")
    assert t.name == "Study MDS"
    assert t.duration == 60
    assert t.category == "study"


def test_task_manager_add_and_list():
    m = TaskManager()
    t1 = Task("Email", 20)
    t2 = Task("Read", 30)

    m.add_task(t1)
    m.add_task(t2)

    all_tasks = m.list_tasks()
    assert len(all_tasks) == 2
    assert all_tasks[0].name == "Email"
    assert all_tasks[1].name == "Read"
