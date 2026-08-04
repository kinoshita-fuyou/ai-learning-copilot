from datetime import date

from app import data
from app.schemas import Period
from app.tools import (
    TOOL_BY_NAME,
    execute_plan,
    execute_tool,
    parse_period,
)


def test_query_sales_covers_period() -> None:
    period = Period(start=date(2026, 8, 1), end=date(2026, 8, 3))

    rows = TOOL_BY_NAME["query_sales"].fn(period.model_dump())

    assert len(rows) == 3 * len(data.REGIONS)
    assert {row["date"] for row in rows} == {"2026-08-01", "2026-08-02", "2026-08-03"}
    assert all(row["amount"] > 0 and row["orders"] > 0 for row in rows)


def test_query_sales_rejects_inverted_period() -> None:
    result = execute_tool(
        "query_sales",
        {"period": {"start": "2026-08-03", "end": "2026-08-01"}},
        simulate_failure=set(),
    )

    assert result["ok"] is False
    assert "period" in result["error"]


def test_compute_totals_math() -> None:
    records = [
        {"region": "华东", "amount": 3000, "orders": 10},
        {"region": "华南", "amount": 5000, "orders": 15},
        {"region": "华北", "amount": 2000, "orders": 5},
    ]

    totals = TOOL_BY_NAME["compute_totals"].fn(records=records)

    assert totals == {
        "total_amount": 10000,
        "total_orders": 30,
        "avg_order_value": round(10000 / 30, 2),
        "top_region": "华南",
    }


def test_query_tasks_rejects_unknown_status() -> None:
    result = execute_tool("query_tasks", {"status": "已取消"}, simulate_failure=set())

    assert result["ok"] is False
    assert "unknown task status" in result["error"]


def test_simulated_failure_retries_then_fails() -> None:
    result = execute_tool(
        "query_tasks",
        {},
        simulate_failure={"query_tasks"},
    )

    assert result["ok"] is False
    assert result["retries"] == 1
    assert "simulated failure" in result["error"]


def test_unknown_tool_is_reported() -> None:
    result = execute_tool("no_such_tool", {}, simulate_failure=set())

    assert result["ok"] is False
    assert "unknown tool" in result["error"]


def test_execute_plan_resolves_refs_in_order() -> None:
    calls = [
        ("query_sales", {"period": {"start": "2026-08-01", "end": "2026-08-01"}}),
        ("compute_totals", {"records": {"$ref": "query_sales"}}),
    ]

    outputs, records = execute_plan(calls, simulate_failure=set())

    assert records[0].ok and records[1].ok
    assert outputs["compute_totals"]["total_orders"] == sum(
        row["orders"] for row in outputs["query_sales"]
    )


def test_parse_period_default() -> None:
    start, end = data.default_period()

    period = parse_period(None, default=(start, end))

    assert period.start == start
    assert period.end == end
