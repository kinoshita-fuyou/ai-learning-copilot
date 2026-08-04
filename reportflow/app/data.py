"""Deterministic mock business data for the demo tools."""

from datetime import date, timedelta


REGIONS = ["华东", "华南", "华北", "西南"]

TASKS = [
    {"id": 1, "title": "订单导出功能联调", "status": "已完成", "owner": "张伟", "due": "2026-07-30"},
    {"id": 2, "title": "埋点数据校验脚本", "status": "已完成", "owner": "李娜", "due": "2026-08-01"},
    {"id": 3, "title": "客户标签模型 v2 训练", "status": "进行中", "owner": "王强", "due": "2026-08-08"},
    {"id": 4, "title": "报表导出接口限流", "status": "进行中", "owner": "刘洋", "due": "2026-08-10"},
    {"id": 5, "title": "新版登录页灰度", "status": "待开始", "owner": "陈静", "due": "2026-08-12"},
    {"id": 6, "title": "权限模块安全评审", "status": "待开始", "owner": "赵敏", "due": "2026-08-15"},
]

INCIDENTS = [
    {"id": 101, "title": "支付回调偶发超时", "severity": "P1", "owner": "后端组", "date": "2026-07-29"},
    {"id": 102, "title": "报表导出慢查询", "severity": "P2", "owner": "数据组", "date": "2026-07-31"},
    {"id": 103, "title": "CDN 配置误改导致静态资源 5xx", "severity": "P0", "owner": "SRE", "date": "2026-08-02"},
    {"id": 104, "title": "搜索索引重建任务失败", "severity": "P2", "owner": "搜索组", "date": "2026-08-03"},
]


def sales_for(start: date, end: date) -> list[dict]:
    """Synthesize deterministic sales rows for every day in [start, end]."""
    rows = []
    day = start
    while day <= end:
        for region_index, region in enumerate(REGIONS):
            seed = day.toordinal() * 17 + region_index * 29
            amount = (seed % 80 + 20) * 1000
            orders = seed % 40 + 5
            rows.append(
                {
                    "date": day.isoformat(),
                    "region": region,
                    "amount": amount,
                    "orders": orders,
                }
            )
        day += timedelta(days=1)
    return rows


def tasks_for(status: str | None = None) -> list[dict]:
    if status is None:
        return TASKS
    return [task for task in TASKS if task["status"] == status]


def incidents_for(start: date, end: date) -> list[dict]:
    return [
        incident
        for incident in INCIDENTS
        if start <= date.fromisoformat(incident["date"]) <= end
    ]


def default_period() -> tuple[date, date]:
    today = date.today()
    return today - timedelta(days=6), today
