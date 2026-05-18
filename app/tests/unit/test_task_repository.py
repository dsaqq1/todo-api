
import pytest
from src.models.task import TaskCreate, TaskPriority, TaskUpdate
from src.repositories.task_repository import TaskRepository
from tests.conftest import make_task_record


@pytest.fixture
def repo(mock_pool_connection) -> TaskRepository:
    pool, _ = mock_pool_connection
    return TaskRepository(pool)


@pytest.mark.asyncio
async def test_find_all(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    connection.fetch.return_value = [make_task_record()]

    records = await repo.find_all()

    assert len(records) == 1
    connection.fetch.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_by_id(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    connection.fetchrow.return_value = make_task_record(id=7)

    record = await repo.find_by_id(7)

    assert record["id"] == 7


@pytest.mark.asyncio
async def test_create(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    connection.fetchrow.return_value = make_task_record(title="Created")
    data = TaskCreate(title="Created", priority=TaskPriority.LOW)

    record = await repo.create(data)

    assert record["title"] == "Created"


@pytest.mark.asyncio
async def test_update_returns_none_when_missing(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    connection.fetchrow.return_value = None

    result = await repo.update(404, TaskUpdate(title="Ghost"))

    assert result is None


@pytest.mark.asyncio
async def test_update_merges_fields(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    current = make_task_record(title="Old", priority="low")
    updated = make_task_record(title="New", priority="high")

    connection.fetchrow.side_effect = [current, updated]

    result = await repo.update(1, TaskUpdate(title="New", priority=TaskPriority.HIGH))

    assert result["title"] == "New"
    assert connection.fetchrow.await_count == 2


@pytest.mark.asyncio
async def test_delete_success(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    connection.execute.return_value = "DELETE 1"

    deleted = await repo.delete(1)

    assert deleted is True


@pytest.mark.asyncio
async def test_delete_not_found(repo, mock_pool_connection):
    _, connection = mock_pool_connection
    connection.execute.return_value = "DELETE 0"

    deleted = await repo.delete(1)

    assert deleted is False
