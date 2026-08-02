"""Seed the demo database with the bundled sample documents.

Usage:
    python scripts/seed_demo.py [--db PATH]

The database file at PATH is rebuilt from scratch (default: evidenceqa.db
in the project root, or $EVIDENCEQA_DB_PATH if set).
"""

import argparse
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.chunking import chunk_text, normalize_text  # noqa: E402
from app.database import init_db  # noqa: E402
from app.embeddings import HashingEmbedder  # noqa: E402
from app.repository import create_document, get_document, replace_document_chunks  # noqa: E402


DATA_DIR = BASE_DIR / "data"
DEFAULT_DB = Path(os.getenv("EVIDENCEQA_DB_PATH", str(BASE_DIR / "evidenceqa.db")))
DEMO_SOURCES = [
    "demo_policy.md",
    "demo_product_manual.md",
    "demo_engineering_guide.md",
]


def seed_demo_db(db_path: Path | None = None) -> list[dict]:
    """Rebuild a fresh demo database and return the created documents."""
    path = Path(db_path or DEFAULT_DB)
    if path.exists():
        path.unlink()
    init_db(path)

    embedder = HashingEmbedder()
    documents = []
    for source_name in DEMO_SOURCES:
        content = (DATA_DIR / source_name).read_text(encoding="utf-8")
        normalized = normalize_text(content)
        document = create_document(
            title=Path(source_name).stem,
            source_name=source_name,
            content_type="text/markdown",
            content=normalized,
            db_path=path,
        )
        replace_document_chunks(
            document_id=document["id"],
            chunks=chunk_text(normalized),
            embedder=embedder,
            db_path=path,
        )
        documents.append(get_document(document["id"], path))
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the demo database.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    args = parser.parse_args()

    documents = seed_demo_db(Path(args.db))
    print(f"已重建演示数据库：{args.db}")
    for document in documents:
        print(
            f"  - {document['title']} "
            f"({document['content_length']} 字符, {document['chunk_count']} 个片段)"
        )
    print("评测集：data/eval_set.json（20 道题，覆盖 3 份文档）")


if __name__ == "__main__":
    main()
