from datetime import datetime

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    title: str
    source_name: str
    content_type: str
    content_length: int
    chunk_count: int
    created_at: datetime


class DocumentChunkOut(BaseModel):
    id: int
    chunk_index: int
    content: str
    char_start: int
    char_end: int
    created_at: datetime


class SearchHit(BaseModel):
    chunk_id: int
    document_id: int
    title: str
    source_name: str
    chunk_index: int
    content: str
    char_start: int
    char_end: int
    score: float


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: list[SearchHit]
