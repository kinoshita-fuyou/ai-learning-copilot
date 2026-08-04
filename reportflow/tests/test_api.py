from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "reportflow"}


def test_list_tools() -> None:
    response = client.get("/tools")

    assert response.status_code == 200
    names = {tool["name"] for tool in response.json()}
    assert names == {"query_sales", "query_tasks", "query_incidents", "compute_totals"}


def test_create_report() -> None:
    response = client.post(
        "/report",
        json={
            "task": "生成本周销售周报",
            "period": {"start": "2026-08-01", "end": "2026-08-03"},
        },
    )

    assert response.status_code == 200
    report = response.json()
    assert report["mode"] == "rule"
    assert report["fallback"] is False
    assert report["tool_stats"]["total"] == 2
    assert report["title"].startswith("生成本周销售周报")


def test_empty_task_rejected() -> None:
    response = client.post("/report", json={"task": ""})

    assert response.status_code == 422


def test_simulate_failure_via_api() -> None:
    response = client.post(
        "/report",
        json={"task": "生成本周销售周报", "simulate_failure": ["compute_totals"]},
    )

    assert response.status_code == 200
    report = response.json()
    assert report["degraded"] is True
    assert report["tool_stats"]["failed"] == 1
