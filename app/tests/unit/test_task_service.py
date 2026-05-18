from unittest.mock import AsyncMock

import pytest
from src.models.task import TaskCreate, TaskPriority, TaskUpdate
from src.services.task_service import TaskNotFoundError, TaskService
from tests.conftest import make_task_record


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repository: AsyncMock) -> TaskService:
    return TaskService(repository)


@pytest.mark.asyncio
async def test_list_tasks_returns_mapped_responses(service, repository):
    repository.find_all.return_value = [
        make_task_record(id=1),
        make_task_record(id=2, title="B"),
    ]

    result = await service.list_tasks()

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].title == "B"


@pytest.mark.asyncio
async def test_get_task_success(service, repository):
    repository.find_by_id.return_value = make_task_record(id=5)

    task = await service.get_task(5)

    assert task.id == 5
    repository.find_by_id.assert_awaited_once_with(5)


@pytest.mark.asyncio
async def test_get_task_not_found(service, repository):
    repository.find_by_id.return_value = None

    with pytest.raises(TaskNotFoundError, match="Task 99 not found"):
        await service.get_task(99)


@pytest.mark.asyncio
async def test_create_task(service, repository):
    repository.create.return_value = make_task_record(title="New")
    payload = TaskCreate(title="New", priority=TaskPriority.HIGH)

    task = await service.create_task(payload)

    assert task.title == "New"
    repository.create.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_update_task_success(service, repository):
    repository.update.return_value = make_task_record(title="Updated")
    payload = TaskUpdate(title="Updated")

    task = await service.update_task(1, payload)

    assert task.title == "Updated"


@pytest.mark.asyncio
async def test_update_task_not_found(service, repository):
    repository.update.return_value = None

    with pytest.raises(TaskNotFoundError):
        await service.update_task(1, TaskUpdate(completed=True))


@pytest.mark.asyncio
async def test_delete_task_success(service, repository):
    repository.delete.return_value = True

    await service.delete_task(3)

    repository.delete.assert_awaited_once_with(3)


@pytest.mark.asyncio
async def test_delete_task_not_found(service, repository):
    repository.delete.return_value = False

    with pytest.raises(TaskNotFoundError):
        await service.delete_task(3)
