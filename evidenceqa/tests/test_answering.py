from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.answering import TemplateAnswerer, get_answer_provider
from app.database import init_db
from app.main import app


def test_template_override_wins_over_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("EVIDENCEQA_ANSWER_PROVIDER", "template")

    assert isinstance(get_answer_provider(), TemplateAnswerer)


def test_invalid_override_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EVIDENCEQA_ANSWER_PROVIDER", "bogus")

    with pytest.raises(RuntimeError, match="Unknown"):
        get_answer_provider()


def test_llm_override_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EVIDENCEQA_ANSWER_PROVIDER", "llm")

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        get_answer_provider()


def test_ask_returns_502_when_provider_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    app.state.db_path = db_path

    class BrokenProvider:
        def answer(self, question: str, contexts: list[dict]) -> None:
            raise ConnectionError("provider down")

    monkeypatch.setattr("app.main.answer_provider", BrokenProvider())
    client = TestClient(app)
    client.post(
        "/documents/upload",
        files={"file": ("policy.md", "远程办公需提前一周申请。".encode(), "text/markdown")},
    )

    response = client.post("/ask", json={"question": "远程办公申请", "top_k": 3})

    assert response.status_code == 502
    assert "provider down" in response.json()["detail"]
