from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from app.database import get_connection
from app.schemas import TaskCreate, TaskUpdate


def _row_to_dict(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["completed"] = bool(item["completed"])
    return item


def create_task(payload: TaskCreate, db_path: Path | None = None) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, description, category, priority, completed, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (
                payload.title,
                payload.description,
                payload.category,
                payload.priority,
                created_at,
            ),
        )
        task_id = cursor.lastrowid
    task = get_task(task_id, db_path)
    if task is None:
        raise RuntimeError("Task was created but could not be read back.")
    return task


def list_tasks(
    completed: bool | None = None,
    category: str | None = None,
    db_path: Path | None = None,
) -> list[dict]:
    sql = "SELECT * FROM tasks"
    values: list[object] = []
    filters: list[str] = []

    if completed is not None:
        filters.append("completed = ?")
        values.append(int(completed))

    if category:
        filters.append("category = ?")
        values.append(category)

    if filters:
        sql += " WHERE " + " AND ".join(filters)

    sql += " ORDER BY completed ASC, priority DESC, id DESC"

    with get_connection(db_path) as connection:
        rows = connection.execute(sql, values).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_task(task_id: int, db_path: Path | None = None) -> dict | None:
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_dict(row) if row else None


def update_task(task_id: int, payload: TaskUpdate, db_path: Path | None = None) -> dict | None:
    current = get_task(task_id, db_path)
    if current is None:
        return None

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return current

    columns: list[str] = []
    values: list[object] = []
    for key, value in changes.items():
        columns.append(f"{key} = ?")
        values.append(int(value) if key == "completed" else value)
    values.append(task_id)

    with get_connection(db_path) as connection:
        connection.execute(
            f"UPDATE tasks SET {', '.join(columns)} WHERE id = ?",
            values,
        )

    return get_task(task_id, db_path)


def delete_task(task_id: int, db_path: Path | None = None) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0


def get_stats(db_path: Path | None = None) -> dict:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(completed), 0) AS completed
            FROM tasks
            """
        ).fetchone()

    total = int(row["total"])
    completed = int(row["completed"])
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
    }

