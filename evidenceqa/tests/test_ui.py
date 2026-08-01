from pathlib import Path

from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


def make_client(tmp_path: Path) -> TestClient:
    app.state.db_path = tmp_path / "test.db"
    init_db(app.state.db_path)
    return TestClient(app)


def test_root_serves_web_console(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "EvidenceQA" in response.text
    assert "static/app.js" in response.text
    assert 'id="dropzone"' in response.text


def test_static_assets_are_served(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    javascript = client.get("/static/app.js")
    stylesheet = client.get("/static/style.css")

    assert javascript.status_code == 200
    assert "renderDocuments" in javascript.text
    assert stylesheet.status_code == 200
    assert "--accent" in stylesheet.text


def test_demo_eval_set_is_served(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/eval/demo")

    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 8
    assert all(
        {"question", "relevant_document_title"} <= set(item) for item in items
    )


def test_console_flow_through_api(tmp_path: Path) -> None:
    """Documents uploaded from the console are immediately askable."""
    client = make_client(tmp_path)
    client.post(
        "/documents/upload",
        files={"file": ("policy.md", "远程办公需要提前一周申请并填写审批表。".encode(), "text/markdown")},
    )

    response = client.post("/ask", json={"question": "远程办公需要提前多久申请", "top_k": 3})

    assert response.status_code == 200
    data = response.json()
    assert data["sources"][0]["title"] == "policy"
