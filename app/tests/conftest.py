import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("DB_USER", "testuser")
os.environ.setdefault("DB_PASSWORD", "testpass")
os.environ.setdefault("DB_HOST", "localhost")


def make_task_record(**overrides) -> dict:
    now = datetime.now(UTC)
    data = {
        "id": 1,
        "title": "Sample task",
        "description": "Details",
        "priority": "medium",
        "due_date": None,
        "completed": False,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return data


@pytest.fixture
def mock_db_pool() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(mock_db_pool: MagicMock) -> TestClient:
    with (
        patch("src.database.init_db", new_callable=AsyncMock),
        patch(
            "src.database.get_pool",
            new_callable=AsyncMock,
            return_value=mock_db_pool,
        ),
        patch("src.database.close_db", new_callable=AsyncMock),
    ):
        from src.main import create_app

        application = create_app()
        with TestClient(application) as test_client:
            yield test_client


@pytest.fixture
def mock_pool_connection() -> tuple[MagicMock, AsyncMock]:
    pool = MagicMock()
    connection = AsyncMock()

    @asynccontextmanager
    async def acquire() -> AsyncIterator[AsyncMock]:
        yield connection

    pool.acquire = acquire
    return pool, connection
