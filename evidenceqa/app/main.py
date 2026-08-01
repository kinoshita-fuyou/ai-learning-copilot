from contextlib import asynccontextmanager
import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.chunking import chunk_text, normalize_text
from app.database import DB_PATH, init_db
from app.embeddings import HashingEmbedder
from app.repository import (
    backfill_chunk_embeddings,
    create_document,
    delete_document,
    get_document,
    list_document_chunks,
    list_documents,
    replace_document_chunks,
)
from app.retrieval import search_chunks
from app.answering import get_answer_provider
from app.evaluation import run_retrieval_eval, EvalQuery
from app.schemas import (
    DocumentChunkOut, DocumentOut, SearchHit,
    AskRequest, AskResponse, EvalQueryItem, EvalResultOut,
    EvalDetailOut, EvalHitShort,
)


ALLOWED_EXTENSIONS = {".md", ".txt"}
MAX_DOCUMENT_BYTES = 1_000_000
STATIC_DIR = Path(__file__).resolve().parent / "static"
EVAL_SET_PATH = Path(__file__).resolve().parent.parent / "data" / "eval_set.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = Path(app.state.db_path)
    init_db(db_path)
    backfill_chunk_embeddings(embedder, db_path)
    yield


app = FastAPI(
    title="EvidenceQA API",
    description="可追溯企业知识库问答系统，包含文档接入、检索、RAG 问答与评测。",
    version="0.4.0",
    lifespan=lifespan,
)
app.state.db_path = DB_PATH
embedder = HashingEmbedder()
answer_provider = get_answer_provider()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "evidenceqa-api"}


@app.get("/", include_in_schema=False)
def web_console() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/eval/demo", response_model=list[EvalQueryItem])
def api_eval_demo_set() -> list[dict]:
    with open(EVAL_SET_PATH, encoding="utf-8") as handle:
        return json.load(handle)


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

    normalized_content = normalize_text(content)
    if not normalized_content:
        raise HTTPException(status_code=422, detail="Document must contain readable text.")

    title = Path(source_name).stem
    document = create_document(
        title=title,
        source_name=source_name,
        content_type=file.content_type or "text/plain",
        content=normalized_content,
        db_path=app.state.db_path,
    )
    replace_document_chunks(
        document_id=document["id"],
        chunks=chunk_text(normalized_content),
        embedder=embedder,
        db_path=app.state.db_path,
    )
    return get_document(document["id"], app.state.db_path)


@app.get("/search", response_model=list[SearchHit])
def api_search(
    q: str = Query(..., min_length=1, max_length=500),
    top_k: int = Query(5, ge=1, le=20),
) -> list[dict]:
    return search_chunks(query=q, embedder=embedder, top_k=top_k, db_path=app.state.db_path)


@app.get("/documents", response_model=list[DocumentOut])
def api_list_documents() -> list[dict]:
    return list_documents(app.state.db_path)


@app.get("/documents/{document_id}", response_model=DocumentOut)
def api_get_document(document_id: int) -> dict:
    document = get_document(document_id, app.state.db_path)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.get("/documents/{document_id}/chunks", response_model=list[DocumentChunkOut])
def api_list_document_chunks(document_id: int) -> list[dict]:
    if get_document(document_id, app.state.db_path) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return list_document_chunks(document_id, app.state.db_path)


@app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_document(document_id: int) -> None:
    deleted = delete_document(document_id, app.state.db_path)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

@app.post("/ask", response_model=AskResponse)
def api_ask(request: AskRequest) -> dict:
    contexts = search_chunks(
        query=request.question,
        embedder=embedder,
        top_k=request.top_k,
        db_path=app.state.db_path,
    )
    result = answer_provider.answer(request.question, contexts)
    return {"answer": result.answer, "sources": result.sources}

@app.post("/eval/retrieval", response_model=EvalResultOut)
def api_eval_retrieval(
    queries: list[EvalQueryItem],
    k: int = Query(5, ge=1, le=20),
) -> dict:
    eval_queries = [EvalQuery(question=q.question, relevant_document_title=q.relevant_document_title) for q in queries]
    metrics = run_retrieval_eval(
        eval_queries=eval_queries,
        embedder=embedder,
        k=k,
        db_path=app.state.db_path,
    )
    return {
        "recall_at_k": metrics.recall_at_k,
        "mrr": metrics.mrr,
        "avg_latency_ms": metrics.avg_latency_ms,
        "total_queries": metrics.total_queries,
        "k": metrics.k,
        "details": metrics.details,
    }


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
