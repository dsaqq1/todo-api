from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from src.models.task import TaskCreate, TaskPriority, TaskUpdate


def test_task_create_defaults():
    task = TaskCreate(title="Buy milk")

    assert task.priority == TaskPriority.MEDIUM
    assert task.completed is False
    assert task.description is None


def test_task_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_task_update_allows_partial_fields():
    update = TaskUpdate(completed=True)

    assert update.title is None
    assert update.completed is True


def test_task_create_with_due_date():
    due = datetime(2026, 6, 1, tzinfo=UTC)
    task = TaskCreate(title="Deadline", due_date=due, priority=TaskPriority.HIGH)

    assert task.due_date == due
    assert task.priority == TaskPriority.HIGH
