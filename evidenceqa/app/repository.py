from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from app.database import get_connection
from app.chunking import TextChunk


def create_document(
    title: str,
    source_name: str,
    content_type: str,
    content: str,
    db_path: Path | None = None,
) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO documents (
                title, source_name, content_type, content, content_length, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, source_name, content_type, content, len(content), created_at),
        )
        document_id = cursor.lastrowid
    document = get_document(document_id, db_path)
    if document is None:
        raise RuntimeError("Document was created but could not be read back.")
    return document


def list_documents(db_path: Path | None = None) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                documents.id,
                documents.title,
                documents.source_name,
                documents.content_type,
                documents.content_length,
                documents.created_at,
                COUNT(chunks.id) AS chunk_count
            FROM documents
            LEFT JOIN chunks ON chunks.document_id = documents.id
            GROUP BY documents.id
            ORDER BY documents.id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_document(document_id: int, db_path: Path | None = None) -> dict | None:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                documents.id,
                documents.title,
                documents.source_name,
                documents.content_type,
                documents.content_length,
                documents.created_at,
                COUNT(chunks.id) AS chunk_count
            FROM documents
            LEFT JOIN chunks ON chunks.document_id = documents.id
            WHERE documents.id = ?
            GROUP BY documents.id
            """,
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def replace_document_chunks(
    document_id: int,
    chunks: list[TextChunk],
    db_path: Path | None = None,
) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    rows = [
        (document_id, index, chunk.content, chunk.char_start, chunk.char_end, created_at)
        for index, chunk in enumerate(chunks)
    ]
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        connection.executemany(
            """
            INSERT INTO chunks (document_id, chunk_index, content, char_start, char_end, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def list_document_chunks(document_id: int, db_path: Path | None = None) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, chunk_index, content, char_start, char_end, created_at
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index
            """,
            (document_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_document(document_id: int, db_path: Path | None = None) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    return cursor.rowcount > 0
