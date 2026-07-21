from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    category: str = Field(default="backend", max_length=50)
    priority: int = Field(default=2, ge=1, le=5)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=50)
    priority: int | None = Field(default=None, ge=1, le=5)
    completed: bool | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: int
    completed: bool
    created_at: datetime


class StatsOut(BaseModel):
    total: int
    completed: int
    pending: int

