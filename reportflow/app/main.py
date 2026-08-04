"""ReportFlow API: turn a business task into a structured report."""

from fastapi import FastAPI

from app.agent import RuleAgent, get_agent
from app.schemas import Report, ReportRequest, ToolInfo
from app.tools import TOOL_SPECS
from app.workflow import run_report


app = FastAPI(
    title="ReportFlow",
    description="结构化报告 Agent：规划 → 工具调用 → 校验 → 生成，失败自动降级。",
    version="1.0.0",
)


def _select_agent() -> object:
    try:
        return get_agent()
    except RuntimeError:
        # 配置不合法（如 llm 模式缺 Key）时回退到离线规则代理
        return RuleAgent()


app.state.agent = _select_agent()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "reportflow"}


@app.get("/tools", response_model=list[ToolInfo])
def list_tools() -> list[ToolInfo]:
    return [
        ToolInfo(name=spec.name, description=spec.description, parameters=spec.parameters)
        for spec in TOOL_SPECS
    ]


@app.post("/report", response_model=Report)
def create_report(request: ReportRequest) -> Report:
    return run_report(request, app.state.agent)
