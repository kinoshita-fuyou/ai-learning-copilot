"""Request/response models for the ReportFlow API."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class Period(BaseModel):
    start: date
    end: date


class ReportRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=200)
    period: Period | None = None
    simulate_failure: list[str] = Field(
        default_factory=list,
        description="Tool names that should fail, to demonstrate degrade-and-continue.",
    )


class Metric(BaseModel):
    label: str
    value: str


class Section(BaseModel):
    heading: str
    metrics: list[Metric] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    table: list[dict] | None = None


class ReportDraft(BaseModel):
    """The structured output the agent must produce."""

    title: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    sections: list[Section] = Field(default_factory=list)


class ToolCallRecord(BaseModel):
    tool: str
    ok: bool
    retries: int = 0
    error: str | None = None


class Report(ReportDraft):
    mode: Literal["rule", "llm"]
    fallback: bool = False
    degraded: bool = False
    tool_stats: dict = Field(default_factory=dict)
    generated_at: datetime


class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: dict
