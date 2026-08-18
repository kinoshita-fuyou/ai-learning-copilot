from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from scripts.seed_demo import seed_demo_db


def make_client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "demo.db"
    seed_demo_db(db_path)
    app.state.db_path = db_path
    return TestClient(app)


def test_hybrid_search_fixes_keyword_question(tmp_path: Path) -> None:
    """Hybrid retrieval should beat vector-only on a keyword-heavy question."""
    client = make_client(tmp_path)
    question = "客户信息可以通过什么方式传输"

    hybrid = client.get("/search", params={"q": question, "top_k": 5, "hybrid": True})
    vector = client.get("/search", params={"q": question, "top_k": 5, "hybrid": False})

    assert hybrid.status_code == 200
    assert vector.status_code == 200
    assert hybrid.json()[0]["title"] == "demo_policy"
    assert vector.json()[0]["title"] != "demo_policy"


def test_eval_supports_vector_and_hybrid_modes(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    eval_set = [
        {"question": "客户信息可以通过什么方式传输", "relevant_document_title": "demo_policy"},
        {"question": "单个文件上传大小上限是多少", "relevant_document_title": "demo_product_manual"},
        {"question": "P0 故障需要在多长时间内响应", "relevant_document_title": "demo_engineering_guide"},
    ]

    hybrid = client.post("/eval/retrieval?mode=hybrid", json=eval_set)
    vector = client.post("/eval/retrieval?mode=vector", json=eval_set)

    assert hybrid.status_code == 200
    assert vector.status_code == 200
    assert hybrid.json()["mode"] == "hybrid"
    assert vector.json()["mode"] == "vector"
    assert hybrid.json()["mrr"] >= vector.json()["mrr"]
    assert hybrid.json()["mrr"] == 1.0
