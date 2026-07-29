"""Retrieval evaluation with recall@k, MRR, and latency metrics."""

import json
import time
from dataclasses import dataclass
from pathlib import Path

from app.embeddings import HashingEmbedder
from app.retrieval import search_chunks


@dataclass
class EvalQuery:
    question: str
    relevant_document_title: str


@dataclass
class EvalMetrics:
    recall_at_k: float
    mrr: float
    avg_latency_ms: float
    total_queries: int
    k: int
    details: list[dict]


def load_eval_set(path: Path) -> list[EvalQuery]:
    with open(path, encoding="utf-8") as f:
        return [EvalQuery(**item) for item in json.load(f)]


def run_retrieval_eval(
    eval_queries: list[EvalQuery],
    embedder: HashingEmbedder,
    k: int = 5,
    db_path: Path | None = None,
) -> EvalMetrics:
    total = len(eval_queries)
    if total == 0:
        return EvalMetrics(
            recall_at_k=1.0, mrr=1.0, avg_latency_ms=0.0,
            total_queries=0, k=k, details=[],
        )

    total_latency = 0.0
    recalls = []
    reciprocal_ranks = []
    details = []

    for q in eval_queries:
        start = time.perf_counter()
        hits = search_chunks(query=q.question, embedder=embedder, top_k=k, db_path=db_path)
        elapsed = (time.perf_counter() - start) * 1000
        total_latency += elapsed

        titles = [h["title"] for h in hits]
        recalled = q.relevant_document_title in titles
        recalls.append(1.0 if recalled else 0.0)

        rr = 0.0
        for idx, title in enumerate(titles, start=1):
            if title == q.relevant_document_title:
                rr = 1.0 / idx
                break
        reciprocal_ranks.append(rr)

        details.append(
            {
                "question": q.question,
                "expected": q.relevant_document_title,
                "recalled": recalled,
                "rr": round(rr, 4),
                "hits": [{"title": h["title"], "score": h["score"]} for h in hits[:3]],
                "latency_ms": round(elapsed, 2),
            }
        )

    return EvalMetrics(
        recall_at_k=round(sum(recalls) / total, 4),
        mrr=round(sum(reciprocal_ranks) / total, 4),
        avg_latency_ms=round(total_latency / total, 2),
        total_queries=total,
        k=k,
        details=details,
    )
