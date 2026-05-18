from datetime import UTC, datetime

import asyncpg
from src.models.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_all(self) -> list[asyncpg.Record]:
        query = """
            SELECT id, title, description, priority, due_date,
                   completed, created_at, updated_at
            FROM tasks
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                due_date NULLS LAST,
                id
        """
        async with self._pool.acquire() as conn:
            return await conn.fetch(query)

    async def find_by_id(self, task_id: int) -> asyncpg.Record | None:
        query = """
            SELECT id, title, description, priority, due_date,
                   completed, created_at, updated_at
            FROM tasks
            WHERE id = $1
        """
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, task_id)

    async def create(self, data: TaskCreate) -> asyncpg.Record:
        query = """
            INSERT INTO tasks (title, description, priority, due_date, completed)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, title, description, priority, due_date,
                      completed, created_at, updated_at
        """
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                query,
                data.title,
                data.description,
                data.priority.value,
                data.due_date,
                data.completed,
            )

    async def update(self, task_id: int, data: TaskUpdate) -> asyncpg.Record | None:
        current = await self.find_by_id(task_id)
        if current is None:
            return None

        title = data.title if data.title is not None else current["title"]
        description = (
            data.description if data.description is not None else current["description"]
        )
        priority = (
            data.priority.value
            if data.priority is not None
            else current["priority"]
        )
        due_date = data.due_date if data.due_date is not None else current["due_date"]
        completed = (
            data.completed if data.completed is not None else current["completed"]
        )

        query = """
            UPDATE tasks
            SET title = $1,
                description = $2,
                priority = $3,
                due_date = $4,
                completed = $5,
                updated_at = $6
            WHERE id = $7
            RETURNING id, title, description, priority, due_date,
                      completed, created_at, updated_at
        """
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                query,
                title,
                description,
                priority,
                due_date,
                completed,
                datetime.now(UTC),
                task_id,
            )

    async def delete(self, task_id: int) -> bool:
        query = "DELETE FROM tasks WHERE id = $1"
        async with self._pool.acquire() as conn:
            result = await conn.execute(query, task_id)
            return result == "DELETE 1"
