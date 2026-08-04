"""Report pipeline: plan -> execute -> validate -> generate, with fallback."""

from datetime import datetime, timezone
from time import perf_counter

from app.agent import ReportAgent, RuleAgent, get_agent
from app.schemas import Report, ReportRequest, ToolCallRecord
from app.tools import execute_plan


def run_report(
    request: ReportRequest,
    agent: ReportAgent | None = None,
) -> Report:
    """Run the full pipeline and return a validated, structured report."""
    started = perf_counter()
    simulate = set(request.simulate_failure)
    chosen_agent = agent or get_agent()

    def execute_bulk(calls: list[tuple[str, dict]]) -> tuple[dict, list[ToolCallRecord]]:
        return execute_plan(calls, simulate)

    fallback = False
    try:
        draft, records = chosen_agent.run(request, execute_bulk)
        mode = chosen_agent.mode
    except Exception:
        # 生成失败时降级到确定性规则代理，保证请求永远有结果
        rule_agent = RuleAgent()
        draft, records = rule_agent.run(request, execute_bulk)
        mode = rule_agent.mode
        fallback = True

    degraded = fallback or any(not record.ok for record in records)
    elapsed_ms = (perf_counter() - started) * 1000
    tool_stats = {
        "total": len(records),
        "failed": sum(1 for record in records if not record.ok),
        "retries": sum(record.retries for record in records),
        "latency_ms": round(elapsed_ms, 2),
        "mode": mode,
        "fallback": fallback,
    }

    return Report(
        **draft.model_dump(),
        mode=mode,
        fallback=fallback,
        degraded=degraded,
        tool_stats=tool_stats,
        generated_at=datetime.now(timezone.utc),
    )
