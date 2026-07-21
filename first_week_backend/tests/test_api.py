from pathlib import Path

from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


def make_client(tmp_path: Path) -> TestClient:
    app.state.db_path = tmp_path / "test.db"
    init_db(app.state.db_path)
    return TestClient(app)


def test_health_check(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    create_response = client.post(
        "/tasks",
        json={
            "title": "学习 FastAPI 路由",
            "description": "理解 GET 和 POST",
            "category": "backend",
            "priority": 4,
        },
    )
    list_response = client.get("/tasks")

    assert create_response.status_code == 201
    assert create_response.json()["title"] == "学习 FastAPI 路由"
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_update_task_completion_and_stats(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    task = client.post("/tasks", json={"title": "写第一个测试"}).json()

    update_response = client.patch(f"/tasks/{task['id']}", json={"completed": True})
    stats_response = client.get("/stats")

    assert update_response.status_code == 200
    assert update_response.json()["completed"] is True
    assert stats_response.json() == {"total": 1, "completed": 1, "pending": 0}


def test_delete_missing_task_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.delete("/tasks/999")

    assert response.status_code == 404

