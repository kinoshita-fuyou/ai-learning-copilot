"""Top-k chunk retrieval over stored chunk embeddings."""

import json
from pathlib import Path

from app.bm25 import BM25Index
from app.database import get_connection
from app.embeddings import HashingEmbedder, cosine_similarity


def _fetch_chunk_rows(db_path: Path | None) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                chunks.id AS chunk_id,
                chunks.document_id,
                chunks.chunk_index,
                chunks.content,
                chunks.char_start,
                chunks.char_end,
                chunks.embedding,
                documents.title,
                documents.source_name
            FROM chunks
            JOIN documents ON documents.id = chunks.document_id
            WHERE chunks.embedding IS NOT NULL
            """
        ).fetchall()
    return [dict(row) for row in rows]


def _to_hits(rows: list[dict], scores: list[float], top_k: int) -> list[dict]:
    hits = []
    for row, score in zip(rows, scores):
        hits.append(
            {
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "title": row["title"],
                "source_name": row["source_name"],
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "char_start": row["char_start"],
                "char_end": row["char_end"],
                "score": round(score, 4),
            }
        )
    hits.sort(key=lambda hit: hit["score"], reverse=True)
    return hits[:top_k]


def _min_max(values: list[float]) -> list[float]:
    """Normalize to [0, 1]; return zeros when the range is flat."""
    low, high = min(values), max(values)
    if high - low < 1e-12:
        return [0.0] * len(values)
    return [(value - low) / (high - low) for value in values]


def search_chunks(
    query: str,
    embedder: HashingEmbedder,
    top_k: int = 5,
    db_path: Path | None = None,
) -> list[dict]:
    """Vector-only Top-K retrieval (baseline)."""
    rows = _fetch_chunk_rows(db_path)
    query_vector = embedder.embed(query)
    scores = [cosine_similarity(query_vector, json.loads(row["embedding"])) for row in rows]
    return _to_hits(rows, scores, top_k)


def hybrid_search_chunks(
    query: str,
    embedder: HashingEmbedder,
    top_k: int = 5,
    alpha: float = 0.5,
    db_path: Path | None = None,
) -> list[dict]:
    """Hybrid retrieval: BM25 keyword score blended with vector similarity.

    Both score families are min-max normalized to [0, 1] before blending so
    their scales are comparable. ``alpha`` weights the vector score; 1 - alpha
    weights BM25.
    """
    rows = _fetch_chunk_rows(db_path)
    if not rows:
        return []
    query_vector = embedder.embed(query)
    vector_scores = [
        cosine_similarity(query_vector, json.loads(row["embedding"])) for row in rows
    ]
    bm25_scores = BM25Index([row["content"] for row in rows]).score_all(query)

    normalized_vector = _min_max(vector_scores)
    normalized_bm25 = _min_max(bm25_scores)
    blended = [
        alpha * vector + (1 - alpha) * keyword
        for vector, keyword in zip(normalized_vector, normalized_bm25)
    ]
    return _to_hits(rows, blended, top_k)
