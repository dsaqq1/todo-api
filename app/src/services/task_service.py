from src.models.task import TaskCreate, TaskResponse, TaskUpdate
from src.repositories.task_repository import TaskRepository


class TaskNotFoundError(Exception):
    pass


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def list_tasks(self) -> list[TaskResponse]:
        records = await self._repository.find_all()
        return [self._to_response(record) for record in records]

    async def get_task(self, task_id: int) -> TaskResponse:
        record = await self._repository.find_by_id(task_id)
        if record is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self._to_response(record)

    async def create_task(self, data: TaskCreate) -> TaskResponse:
        record = await self._repository.create(data)
        return self._to_response(record)

    async def update_task(self, task_id: int, data: TaskUpdate) -> TaskResponse:
        record = await self._repository.update(task_id, data)
        if record is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self._to_response(record)

    async def delete_task(self, task_id: int) -> None:
        deleted = await self._repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"Task {task_id} not found")

    @staticmethod
    def _to_response(record) -> TaskResponse:
        return TaskResponse(
            id=record["id"],
            title=record["title"],
            description=record["description"],
            priority=record["priority"],
            due_date=record["due_date"],
            completed=record["completed"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
