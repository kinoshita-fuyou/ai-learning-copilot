"""Tests for the retrieval evaluation module."""

from pathlib import Path

from app.embeddings import HashingEmbedder
from app.evaluation import EvalQuery, run_retrieval_eval


def test_eval_empty_queries_returns_perfect():
    embedder = HashingEmbedder()
    result = run_retrieval_eval([], embedder, k=5)
    assert result.recall_at_k == 1.0
    assert result.mrr == 1.0
    assert result.total_queries == 0


def test_eval_with_seeded_data(tmp_path: Path):
    """Integration: upload a doc, run eval, verify metrics make sense."""
    from app.database import init_db, get_connection
    from app.chunking import chunk_text, normalize_text
    from app.repository import create_document, replace_document_chunks

    db = tmp_path / "test.db"
    init_db(db)
    embedder = HashingEmbedder()

    content = normalize_text(
        "## 报销\n差旅报销需要提前审批，发票在三十天内提交。\n\n"
        "## 考勤\n每日 09:00 前签到，迟到需说明原因。"
    )
    doc = create_document("policy", "policy.md", "text/markdown", content, db_path=db)
    replace_document_chunks(doc["id"], chunk_text(content), embedder, db_path=db)

    queries = [
        EvalQuery(question="报销发票提交期限", relevant_document_title="policy"),
        EvalQuery(question="签到截止时间", relevant_document_title="policy"),
    ]
    result = run_retrieval_eval(queries, embedder, k=3, db_path=db)

    assert result.total_queries == 2
    assert result.recall_at_k >= 0.5  # at least one should hit
    assert result.mrr >= 0.5
    assert result.avg_latency_ms > 0
    assert len(result.details) == 2
    assert result.details[0]["hits"]
