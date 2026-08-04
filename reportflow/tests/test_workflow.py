from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import Period, ReportDraft, ReportRequest
from app.workflow import run_report


def make_request(task: str, **kwargs) -> ReportRequest:
    return ReportRequest(
        task=task,
        period=Period(start=date(2026, 8, 1), end=date(2026, 8, 3)),
        **kwargs,
    )


def test_sales_task_produces_structured_report() -> None:
    report = run_report(make_request("生成本周销售周报"))

    assert report.mode == "rule"
    assert report.fallback is False
    assert report.degraded is False
    assert report.tool_stats["total"] == 2
    assert any(section.heading == "销售表现" for section in report.sections)
    assert report.summary
    assert report.generated_at is not None


def test_failure_injection_degrades_instead_of_crashing() -> None:
    report = run_report(
        make_request("生成本周销售周报", simulate_failure=["query_sales"])
    )

    assert report.degraded is True
    # query_sales 模拟失败，compute_totals 因缺少依赖一并记录为失败
    assert report.tool_stats["failed"] == 2
    assert report.tool_stats["retries"] == 1
    assert any(section.heading == "销售表现" for section in report.sections) is False


def test_agent_crash_falls_back_to_rule_agent() -> None:
    class BrokenAgent:
        mode = "llm"

        def run(self, request, execute_bulk):
            raise ConnectionError("model endpoint down")

    report = run_report(make_request("生成本周销售周报"), agent=BrokenAgent())

    assert report.mode == "rule"
    assert report.fallback is True
    assert report.degraded is True
    assert report.summary


@pytest.mark.parametrize(
    ("task", "heading"),
    [
        ("本周线上故障汇总", "稳定性"),
        ("项目进展周报", "项目进展"),
        ("综合运营周报", "销售表现"),
    ],
)
def test_task_classification(task: str, heading: str) -> None:
    report = run_report(make_request(task))

    assert any(section.heading == heading for section in report.sections)


def test_report_draft_enforces_structure() -> None:
    with pytest.raises(ValidationError):
        ReportDraft(title="", summary="x")
