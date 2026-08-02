import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import EVAL_SET_PATH, app
from scripts.seed_demo import DEMO_SOURCES, seed_demo_db


def test_seed_demo_builds_all_documents(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.db"

    documents = seed_demo_db(db_path)

    assert {document["title"] for document in documents} == {
        "demo_policy",
        "demo_product_manual",
        "demo_engineering_guide",
    }
    assert all(document["chunk_count"] > 0 for document in documents)
    assert db_path.exists()


def test_seeded_demo_is_searchable_via_api(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.db"
    seed_demo_db(db_path)
    app.state.db_path = db_path
    client = TestClient(app)

    response = client.get("/search", params={"q": "单个文件上传大小上限"})

    assert response.status_code == 200
    assert response.json()[0]["title"] == "demo_product_manual"


def test_seeded_demo_passes_retrieval_eval(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.db"
    seed_demo_db(db_path)
    app.state.db_path = db_path
    client = TestClient(app)

    eval_set = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))
    response = client.post("/eval/retrieval", json=eval_set)

    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_queries"] == len(eval_set)
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 1.0


def test_demo_eval_set_covers_all_demo_documents() -> None:
    eval_set = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))
    titles = {item["relevant_document_title"] for item in eval_set}
    expected = {source.removesuffix(".md") for source in DEMO_SOURCES}

    assert len(eval_set) >= 15
    assert titles == expected
