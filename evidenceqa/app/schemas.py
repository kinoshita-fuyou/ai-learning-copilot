from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    title: str
    source_name: str
    content_type: str
    content_length: int
    created_at: datetime
