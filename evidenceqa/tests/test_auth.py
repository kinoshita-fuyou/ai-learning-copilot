from pathlib import Path

from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


def make_client(tmp_path: Path, api_key: str | None) -> TestClient:
    app.state.db_path = tmp_path / "test.db"
    init_db(app.state.db_path)
    app.state.api_key = api_key
    return TestClient(app)


def test_auth_disabled_by_default(tmp_path: Path) -> None:
    client = make_client(tmp_path, api_key=None)

    response = client.get("/documents")

    assert response.status_code == 200


def test_protected_endpoint_rejects_missing_key(tmp_path: Path) -> None:
    client = make_client(tmp_path, api_key="secret-key")

    response = client.get("/documents")

    assert response.status_code == 401
    assert "X-API-Key" in response.json()["detail"]


def test_protected_endpoint_rejects_wrong_key(tmp_path: Path) -> None:
    client = make_client(tmp_path, api_key="secret-key")

    response = client.get("/documents", headers={"X-API-Key": "wrong"})

    assert response.status_code == 401


def test_protected_endpoint_accepts_valid_key(tmp_path: Path) -> None:
    client = make_client(tmp_path, api_key="secret-key")

    response = client.get("/documents", headers={"X-API-Key": "secret-key"})

    assert response.status_code == 200


def test_health_and_console_stay_open_when_auth_enabled(tmp_path: Path) -> None:
    client = make_client(tmp_path, api_key="secret-key")

    health = client.get("/health")
    console = client.get("/")

    assert health.status_code == 200
    assert console.status_code == 200


def test_ask_requires_key_when_auth_enabled(tmp_path: Path) -> None:
    client = make_client(tmp_path, api_key="secret-key")

    response = client.post("/ask", json={"question": "远程办公申请"})

    assert response.status_code == 401
