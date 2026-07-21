from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from app.database import DB_PATH, init_db
from app.repository import (
    create_task,
    delete_task,
    get_stats,
    get_task,
    list_tasks,
    update_task,
)
from app.schemas import StatsOut, TaskCreate, TaskOut, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = Path(app.state.db_path)
    init_db(db_path)
    yield


app = FastAPI(
    title="AI Learning Task API",
    description="第一周后端项目：用 FastAPI 管理 AI 学习任务。",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.db_path = DB_PATH


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut, status_code=201)
def api_create_task(payload: TaskCreate) -> dict:
    return create_task(payload, app.state.db_path)


@app.get("/tasks", response_model=list[TaskOut])
def api_list_tasks(
    completed: bool | None = Query(default=None),
    category: str | None = Query(default=None),
) -> list[dict]:
    return list_tasks(completed=completed, category=category, db_path=app.state.db_path)


@app.get("/tasks/{task_id}", response_model=TaskOut)
def api_get_task(task_id: int) -> dict:
    task = get_task(task_id, app.state.db_path)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def api_update_task(task_id: int, payload: TaskUpdate) -> dict:
    task = update_task(task_id, payload, app.state.db_path)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def api_delete_task(task_id: int) -> None:
    deleted = delete_task(task_id, app.state.db_path)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@app.get("/stats", response_model=StatsOut)
def api_get_stats() -> dict:
    return get_stats(app.state.db_path)

