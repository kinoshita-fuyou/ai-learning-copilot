from datetime import datetime

from pydantic import BaseModel


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
