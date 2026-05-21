import sys

from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api.routes.tasks import router as tasks_router
from src.database import close_db, get_pool, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    app.state.db_pool = await get_pool()
    yield
    await close_db()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Todo List API",
        description="Task management system with priorities and due dates",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.include_router(tasks_router)

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    return application


app = create_app()
