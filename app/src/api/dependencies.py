from fastapi import Request
from src.repositories.task_repository import TaskRepository
from src.services.task_service import TaskService


def get_task_service(request: Request) -> TaskService:
    pool = request.app.state.db_pool
    repository = TaskRepository(pool)
    return TaskService(repository)
