"""Top-k chunk retrieval over stored chunk embeddings."""

import json
from pathlib import Path

from app.database import get_connection
from app.embeddings import HashingEmbedder, cosine_similarity


def search_chunks(
    query: str,
    embedder: HashingEmbedder,
    top_k: int = 5,
    db_path: Path | None = None,
) -> list[dict]:
    query_vector = embedder.embed(query)
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

    hits = []
    for row in rows:
        score = cosine_similarity(query_vector, json.loads(row["embedding"]))
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
