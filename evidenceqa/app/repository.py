from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from app.database import get_connection


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
            SELECT id, title, source_name, content_type, content_length, created_at
            FROM documents
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_document(document_id: int, db_path: Path | None = None) -> dict | None:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, title, source_name, content_type, content_length, created_at
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def delete_document(document_id: int, db_path: Path | None = None) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    return cursor.rowcount > 0
