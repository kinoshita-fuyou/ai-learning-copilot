from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.database import DB_PATH, init_db
from app.repository import (
    create_document,
    delete_document,
    get_document,
    list_documents,
)
from app.schemas import DocumentOut


ALLOWED_EXTENSIONS = {".md", ".txt"}
MAX_DOCUMENT_BYTES = 1_000_000


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = Path(app.state.db_path)
    init_db(db_path)
    yield


app = FastAPI(
    title="EvidenceQA API",
    description="可追溯企业知识库问答系统的后端服务。",
    version="0.2.0",
    lifespan=lifespan,
)
app.state.db_path = DB_PATH


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "evidenceqa-api"}


@app.post("/documents/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)) -> dict:
    source_name = file.filename or "untitled"
    extension = Path(source_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .md and .txt documents are supported.",
        )

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=422, detail="Document must not be empty.")
    if len(content_bytes) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Document exceeds the 1 MB size limit.")

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=422,
            detail="Document must use UTF-8 encoding.",
        ) from error

    title = Path(source_name).stem
    return create_document(
        title=title,
        source_name=source_name,
        content_type=file.content_type or "text/plain",
        content=content,
        db_path=app.state.db_path,
    )


@app.get("/documents", response_model=list[DocumentOut])
def api_list_documents() -> list[dict]:
    return list_documents(app.state.db_path)


@app.get("/documents/{document_id}", response_model=DocumentOut)
def api_get_document(document_id: int) -> dict:
    document = get_document(document_id, app.state.db_path)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_document(document_id: int) -> None:
    deleted = delete_document(document_id, app.state.db_path)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
