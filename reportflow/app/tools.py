"""Tool registry and execution with validation and retry."""

from dataclasses import dataclass
from datetime import date
from typing import Callable

from app import data
from app.schemas import Period, ToolCallRecord


class ToolError(Exception):
    """Raised when a tool cannot fulfil its contract."""


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict
    fn: Callable
    validator: Callable | None = None


def _query_sales(period: dict) -> list[dict]:
    period = Period(**period)
    if period.end < period.start:
        raise ToolError("period.end must not be earlier than period.start")
    return data.sales_for(period.start, period.end)


def _query_tasks(status: str | None = None) -> list[dict]:
    allowed = {"已完成", "进行中", "待开始"}
    if status is not None and status not in allowed:
        raise ToolError(f"unknown task status: {status!r} (expected {sorted(allowed)})")
    return data.tasks_for(status)


def _query_incidents(period: dict) -> list[dict]:
    period = Period(**period)
    if period.end < period.start:
        raise ToolError("period.end must not be earlier than period.start")
    return data.incidents_for(period.start, period.end)


def _compute_totals(records: list[dict]) -> dict:
    if not records:
        raise ToolError("compute_totals requires at least one record")
    total_amount = sum(record["amount"] for record in records)
    total_orders = sum(record["orders"] for record in records)
    top_region = max(records, key=lambda record: record["amount"])["region"]
    return {
        "total_amount": total_amount,
        "total_orders": total_orders,
        "avg_order_value": round(total_amount / total_orders, 2) if total_orders else 0,
        "top_region": top_region,
    }


def _validate_rows(result: list[dict]) -> None:
    if not isinstance(result, list):
        raise ToolError("expected a list of rows")
    for row in result:
        if not isinstance(row, dict):
            raise ToolError("each row must be an object")


def _validate_totals(result: dict) -> None:
    if not isinstance(result, dict):
        raise ToolError("expected an object")
    required = {"total_amount", "total_orders", "top_region"}
    missing = required - set(result)
    if missing:
        raise ToolError(f"missing keys: {sorted(missing)}")


PERIOD_SCHEMA = {
    "type": "object",
    "properties": {
        "period": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "ISO date, e.g. 2026-08-01"},
                "end": {"type": "string", "description": "ISO date, e.g. 2026-08-07"},
            },
            "required": ["start", "end"],
        }
    },
}

TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="query_sales",
        description="查询指定日期范围内的销售记录，返回按日期和区域拆分的行。",
        parameters={
            "type": "object",
            "properties": {
                "period": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string", "description": "ISO 日期，如 2026-08-01"},
                        "end": {"type": "string", "description": "ISO 日期，如 2026-08-07"},
                    },
                    "required": ["start", "end"],
                }
            },
            "required": ["period"],
        },
        fn=_query_sales,
        validator=_validate_rows,
    ),
    ToolSpec(
        name="query_tasks",
        description="查询项目任务列表，可按状态过滤（已完成/进行中/待开始）。",
        parameters={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["已完成", "进行中", "待开始"],
                    "description": "可选，按状态过滤",
                }
            },
        },
        fn=_query_tasks,
        validator=_validate_rows,
    ),
    ToolSpec(
        name="query_incidents",
        description="查询指定日期范围内的线上故障/事故记录。",
        parameters=PERIOD_SCHEMA,
        fn=_query_incidents,
        validator=_validate_rows,
    ),
    ToolSpec(
        name="compute_totals",
        description="对销售记录汇总：总金额、总订单、客单价与金额最高的区域。",
        parameters={
            "type": "object",
            "properties": {
                "records": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "query_sales 返回的记录",
                }
            },
            "required": ["records"],
        },
        fn=_compute_totals,
        validator=_validate_totals,
    ),
]

TOOL_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}


def tool_specs_for_openai() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.parameters,
            },
        }
        for spec in TOOL_SPECS
    ]


def execute_tool(name: str, args: dict, simulate_failure: set[str]) -> dict:
    """Run one tool, retry once on failure, and validate its output contract."""
    spec = TOOL_BY_NAME.get(name)
    if spec is None:
        return {"ok": False, "error": f"unknown tool: {name!r}", "retries": 0}

    retries = 0
    attempt = 0
    while True:
        try:
            if name in simulate_failure:
                raise ToolError(f"simulated failure for {name!r}")
            result = spec.fn(**args)
            if spec.validator is not None:
                spec.validator(result)
            return {"ok": True, "result": result, "retries": retries}
        except (ToolError, KeyError, TypeError) as error:
            if attempt < 1:
                attempt += 1
                retries += 1
                continue
            return {"ok": False, "error": str(error), "retries": retries}


def resolve_refs(args: dict, outputs: dict) -> dict:
    """Resolve ``{"$ref": "tool_name"}`` placeholders to earlier tool output."""
    resolved: dict = {}
    for key, value in args.items():
        if isinstance(value, dict) and "$ref" in value:
            resolved[key] = outputs[value["$ref"]]
        elif isinstance(value, dict):
            resolved[key] = resolve_refs(value, outputs)
        else:
            resolved[key] = value
    return resolved


def execute_plan(
    calls: list[tuple[str, dict]],
    simulate_failure: set[str],
) -> tuple[dict[str, object], list[ToolCallRecord]]:
    """Execute (tool, args) calls in order, resolving refs to earlier outputs."""
    outputs: dict[str, object] = {}
    records: list[ToolCallRecord] = []
    for name, args in calls:
        try:
            resolved_args = resolve_refs(args, outputs)
        except KeyError as error:
            records.append(
                ToolCallRecord(
                    tool=name,
                    ok=False,
                    error=f"missing dependency: {error}",
                )
            )
            continue
        result = execute_tool(name, resolved_args, simulate_failure)
        records.append(
            ToolCallRecord(
                tool=name,
                ok=result["ok"],
                retries=result["retries"],
                error=result.get("error"),
            )
        )
        if result["ok"]:
            outputs[name] = result["result"]
    return outputs, records


def parse_period(period: dict | None, default: tuple[date, date]) -> Period:
    if period is None:
        start, end = default
        return Period(start=start, end=end)
    return Period(**period)
