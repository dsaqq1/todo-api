from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from src.api.dependencies import get_task_service
from src.models.task import TaskCreate, TaskPriority, TaskResponse
from src.services.task_service import TaskNotFoundError, TaskService


def _task_response(**overrides) -> TaskResponse:
    now = datetime.now(UTC)
    data = {
        "id": 1,
        "title": "API task",
        "description": None,
        "priority": TaskPriority.MEDIUM,
        "due_date": None,
        "completed": False,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return TaskResponse(**data)


@pytest.fixture
def mock_service() -> AsyncMock:
    service = AsyncMock(spec=TaskService)
    return service


@pytest.fixture
def api_client(client: TestClient, mock_service: AsyncMock) -> TestClient:
    client.app.dependency_overrides[get_task_service] = lambda: mock_service
    yield client
    client.app.dependency_overrides.clear()


def test_health_endpoint(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks(api_client, mock_service):
    mock_service.list_tasks.return_value = [_task_response()]

    response = api_client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "API task"


def test_get_task(api_client, mock_service):
    mock_service.get_task.return_value = _task_response(id=2)

    response = api_client.get("/api/tasks/2")

    assert response.status_code == 200
    assert response.json()["id"] == 2


def test_get_task_not_found(api_client, mock_service):
    mock_service.get_task.side_effect = TaskNotFoundError("missing")

    response = api_client.get("/api/tasks/404")

    assert response.status_code == 404


def test_create_task(api_client, mock_service):
    mock_service.create_task.return_value = _task_response(title="New")

    response = api_client.post(
        "/api/tasks",
        json={"title": "New", "priority": "high"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "New"
    mock_service.create_task.assert_awaited_once()
    call_arg = mock_service.create_task.await_args.args[0]
    assert isinstance(call_arg, TaskCreate)


def test_update_task(api_client, mock_service):
    mock_service.update_task.return_value = _task_response(completed=True)

    response = api_client.put("/api/tasks/1", json={"completed": True})

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_update_task_not_found(api_client, mock_service):
    mock_service.update_task.side_effect = TaskNotFoundError("missing")

    response = api_client.put("/api/tasks/1", json={"title": "X"})

    assert response.status_code == 404


def test_delete_task(api_client, mock_service):
    mock_service.delete_task.return_value = None

    response = api_client.delete("/api/tasks/1")

    assert response.status_code == 204


def test_delete_task_not_found(api_client, mock_service):
    mock_service.delete_task.side_effect = TaskNotFoundError("missing")

    response = api_client.delete("/api/tasks/1")

    assert response.status_code == 404


def test_create_task_validation_error(api_client):
    response = api_client.post("/api/tasks", json={"title": ""})

    assert response.status_code == 422
