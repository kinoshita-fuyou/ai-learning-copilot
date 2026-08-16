"""Report agents.

``RuleAgent`` is a deterministic offline implementation that shares the exact
same interface as ``LLMAgent``, so demos, tests and CI never depend on a
working model endpoint. ``LLMAgent`` performs real tool calling: it decides
which tools to run, observes their results, and finally submits a structured
report through a forced ``generate_report`` call.
"""

import json
import os
from typing import Callable, Protocol

from app import data
from app.schemas import Period, ReportDraft, ReportRequest, Section, Metric
from app.tools import TOOL_BY_NAME, execute_tool, parse_period, tool_specs_for_openai


def _period_args(period: Period) -> dict:
    return {"period": {"start": period.start.isoformat(), "end": period.end.isoformat()}}


class ReportAgent(Protocol):
    mode: str

    def run(self, request: ReportRequest, execute_bulk: Callable) -> tuple[ReportDraft, list]:
        ...


class RuleAgent:
    """Deterministic agent: keyword planning + template generation."""

    mode = "rule"

    def plan(self, request: ReportRequest) -> list[tuple[str, dict]]:
        task = request.task
        period = parse_period(
            request.period.model_dump() if request.period else None,
            data.default_period(),
        )
        period_args = _period_args(period)

        if any(word in task for word in ("故障", "事故", "运维", "稳定性", "线上")):
            return [("query_incidents", period_args)]
        if any(word in task for word in ("项目", "任务", "进展", "研发")):
            return [("query_tasks", {})]
        if any(word in task for word in ("销售", "业绩", "营收", "订单")):
            return [
                ("query_sales", period_args),
                ("compute_totals", {"records": {"$ref": "query_sales"}}),
            ]
        # 综合报告：销售 + 任务
        return [
            ("query_sales", period_args),
            ("compute_totals", {"records": {"$ref": "query_sales"}}),
            ("query_tasks", {}),
        ]

    def generate(self, request: ReportRequest, outputs: dict) -> ReportDraft:
        period = parse_period(
            request.period.model_dump() if request.period else None,
            data.default_period(),
        )
        sections: list[Section] = []
        bullets: list[str] = []

        if "query_sales" in outputs:
            records = outputs["query_sales"]
            per_region: dict[str, dict] = {}
            for record in records:
                region = per_region.setdefault(
                    record["region"], {"amount": 0, "orders": 0}
                )
                region["amount"] += record["amount"]
                region["orders"] += record["orders"]
            table = [
                {"区域": region, "金额": stats["amount"], "订单": stats["orders"]}
                for region, stats in sorted(
                    per_region.items(), key=lambda item: item[1]["amount"], reverse=True
                )
            ]
            if "compute_totals" in outputs:
                totals = outputs["compute_totals"]
                metrics = [
                    Metric(label="总金额", value=f"¥{totals['total_amount']:,}"),
                    Metric(label="总订单", value=str(totals["total_orders"])),
                    Metric(label="客单价", value=f"¥{totals['avg_order_value']:.2f}"),
                    Metric(label="头部区域", value=totals["top_region"]),
                ]
                bullet = f"统计区间 {period.start.isoformat()} 至 {period.end.isoformat()}，金额最高的区域为{totals['top_region']}。"
            else:
                metrics = [
                    Metric(label="记录数", value=str(len(records))),
                    Metric(label="覆盖区域", value=str(len(per_region))),
                ]
                bullet = "汇总工具暂不可用，以下为按区域统计的明细。"
            sections.append(
                Section(
                    heading="销售表现",
                    metrics=metrics,
                    bullets=[bullet],
                    table=table,
                )
            )
            if "compute_totals" in outputs:
                bullets.append(
                    f"周期内销售额 ¥{outputs['compute_totals']['total_amount']:,}，"
                    f"订单 {outputs['compute_totals']['total_orders']} 单。"
                )

        if "query_tasks" in outputs:
            tasks = outputs["query_tasks"]
            counts: dict[str, int] = {}
            for task in tasks:
                counts[task["status"]] = counts.get(task["status"], 0) + 1
            sections.append(
                Section(
                    heading="项目进展",
                    metrics=[
                        Metric(label="任务总数", value=str(len(tasks))),
                        *[
                            Metric(label=f"{status}任务", value=str(count))
                            for status, count in sorted(counts.items())
                        ],
                    ],
                    bullets=[
                        f"进行中：{next((t['title'] for t in tasks if t['status'] == '进行中'), '无')}"
                    ],
                )
            )
            bullets.append(f"任务共 {len(tasks)} 个，进行中 {counts.get('进行中', 0)} 个。")

        if "query_incidents" in outputs:
            incidents = outputs["query_incidents"]
            p0 = sum(1 for item in incidents if item["severity"] == "P0")
            sections.append(
                Section(
                    heading="稳定性",
                    metrics=[
                        Metric(label="故障数", value=str(len(incidents))),
                        Metric(label="P0", value=str(p0)),
                    ],
                    bullets=[
                        f"P0 故障 {p0} 起" + ("，已按应急流程处理。" if p0 else "，本周无 P0。")
                    ],
                    table=[{"标题": i["title"], "级别": i["severity"], "负责人": i["owner"]} for i in incidents],
                )
            )
            bullets.append(f"记录线上故障 {len(incidents)} 起。")

        summary = "；".join(bullets) if bullets else "未检索到相关数据。"
        title = f"{request.task}（{period.start.isoformat()} ~ {period.end.isoformat()}）"
        return ReportDraft(title=title, summary=summary, sections=sections)

    def run(self, request: ReportRequest, execute_bulk: Callable) -> tuple[ReportDraft, list]:
        calls = self.plan(request)
        outputs, records = execute_bulk(calls)
        return self.generate(request, outputs), records


class LLMAgent:
    """Real tool-calling agent over an OpenAI-compatible chat API."""

    mode = "llm"

    def __init__(self, api_key: str, base_url: str | None = None, model: str = "gpt-4o-mini"):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)
        self.model = model

    def run(self, request: ReportRequest, execute_bulk: Callable) -> tuple[ReportDraft, list]:
        from openai import OpenAIError
        from pydantic import ValidationError

        period = parse_period(
            request.period.model_dump() if request.period else None,
            data.default_period(),
        )
        system = (
            "你是 ReportFlow 的报表代理。根据用户任务决定调用哪些工具获取数据，"
            "观察工具结果后，最后必须调用 generate_report 工具提交结构化报告。"
            "报告必须使用中文，内容只能基于工具返回的数据。"
        )
        user = (
            f"任务：{request.task}\n"
            f"统计区间：{period.start.isoformat()} 至 {period.end.isoformat()}\n"
            "先调用需要的工具，全部拿到结果后调用 generate_report。"
        )
        messages: list[dict] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        records: list = []
        validate_budget = 1

        generate_spec = {
            "type": "function",
            "function": {
                "name": "generate_report",
                "description": "提交最终结构化报告（仅此工具可提交报告）。",
                "parameters": ReportDraft.model_json_schema(),
            },
        }

        for _ in range(8):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_specs_for_openai() + [generate_spec],
                tool_choice="auto",
                temperature=0.2,
            )
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if message.tool_calls:
                for call in message.tool_calls:
                    try:
                        args = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    if call.function.name == "generate_report":
                        try:
                            draft = ReportDraft(**args)
                            return draft, records
                        except ValidationError as error:
                            if validate_budget <= 0:
                                raise
                            validate_budget -= 1
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": call.id,
                                    "content": (
                                        f"报告不符合结构要求：{error}。"
                                        "请修正后重新调用 generate_report。"
                                    ),
                                }
                            )
                            continue
                    result = execute_tool(call.function.name, args, simulate_failure=set())
                    records.append(
                        {
                            "tool": call.function.name,
                            "ok": result["ok"],
                            "retries": result["retries"],
                            "error": result.get("error"),
                        }
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(
                                result.get("result") if result["ok"] else {"error": result["error"]},
                                ensure_ascii=False,
                            ),
                        }
                    )
                continue

            # 模型没有调用工具就直接输出文本：强制走 generate_report
            messages.append(
                {
                    "role": "user",
                    "content": "不要直接输出文本，请调用 generate_report 工具提交结构化报告。",
                }
            )

        raise OpenAIError("LLM agent exceeded max rounds without submitting a report")


def get_agent() -> ReportAgent:
    """Select agent: REPORTFLOW_AGENT=rule|llm|auto (default auto)."""
    override = os.getenv("REPORTFLOW_AGENT", "auto").strip().lower()
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("REPORTFLOW_MODEL", "gpt-4o-mini")

    if override == "rule":
        return RuleAgent()
    if override == "llm":
        if not api_key:
            raise RuntimeError("REPORTFLOW_AGENT=llm requires OPENAI_API_KEY to be set.")
        return LLMAgent(api_key=api_key, base_url=base_url, model=model)
    if override != "auto":
        raise RuntimeError(
            f"Unknown REPORTFLOW_AGENT: {override!r} (expected rule, llm or auto)."
        )
    if api_key:
        return LLMAgent(api_key=api_key, base_url=base_url, model=model)
    return RuleAgent()
