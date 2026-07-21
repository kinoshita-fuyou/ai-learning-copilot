# AI Learning Copilot

一个面向 AI 应用开发入门的学习任务后端。它会逐步演进为可检索个人学习资料、生成学习建议的 AI 知识库应用。

第一阶段先不接入大模型，目标是练会后面做 RAG、Agent、AI 工具时一定会用到的后端基本功：

- FastAPI 接口开发
- Pydantic 参数校验
- SQLite 数据库存储
- 分层代码结构
- 自动化测试
- 本地启动脚本

## 新安装/使用的框架和工具

```text
fastapi      Web API 框架，用来写接口
uvicorn      ASGI 服务器，用来运行 FastAPI 项目
pydantic     数据校验与接口模型，FastAPI 内部会用到
pytest       自动化测试框架
httpx        测试接口时使用，FastAPI TestClient 依赖它
```

Python 内置模块：

```text
sqlite3      轻量数据库，不需要额外安装数据库服务
pathlib      处理文件路径
datetime     处理创建时间
```

## 项目功能

```text
GET    /health              健康检查
POST   /tasks               创建学习任务
GET    /tasks               查看任务列表
GET    /tasks/{task_id}     查看单个任务
PATCH  /tasks/{task_id}     更新任务
DELETE /tasks/{task_id}     删除任务
GET    /stats               查看任务统计
```

## 开发路线

```text
Day 1: 学习任务 API、SQLite、测试
Day 2: 学习资料上传与元数据管理
Day 3: 文本提取与切分
Day 4: Embedding 和向量检索
Day 5: RAG 问答接口与引用溯源
Day 6: 检索质量优化与评测集
Day 7: 简单 Web 界面
Day 8: Docker 部署与环境配置
Day 9: 面试材料、架构图与演示数据
Day 10: 压测、整理 README、模拟面试
```

## 目录结构

```text
first_week_backend/
  app/
    __init__.py
    main.py        FastAPI 应用入口
    database.py    数据库连接和初始化
    schemas.py     请求/响应数据模型
    repository.py  数据库读写逻辑
  tests/
    test_api.py    接口测试
  scripts/
    start.sh       启动服务
    test.sh        运行测试
  requirements.txt
  pyproject.toml   pytest 配置
  README.md
```

## 启动方式

进入项目目录：

```bash
cd /Users/a1-6/Documents/Codex/2026-06-14/ai/first_week_backend
```

创建虚拟环境：

```bash
python3 -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务。这里使用 8001 端口，因为你的电脑上 8000 端口已经被其他本地服务占用了：

```bash
./scripts/start.sh
```

打开接口文档：

```text
http://127.0.0.1:8001/docs
```

## 运行测试

```bash
./scripts/test.sh
```

## 手动测试接口

健康检查：

```bash
curl http://127.0.0.1:8001/health
```

创建任务：

```bash
curl -X POST http://127.0.0.1:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"学习 FastAPI","priority":4}'
```

查看任务：

```bash
curl http://127.0.0.1:8001/tasks
```

## 推荐学习顺序

1. 先打开 `app/main.py`，理解每个接口长什么样。
2. 再看 `app/schemas.py`，理解请求数据和响应数据如何被定义。
3. 然后看 `app/repository.py`，理解数据是怎么写入 SQLite 的。
4. 最后看 `tests/test_api.py`，理解如何验证接口是否正确。

## 你应该掌握到什么程度

完成第一周后，你应该能独立回答：

- 什么是 API？
- GET、POST、PATCH、DELETE 分别适合做什么？
- FastAPI 的路由是怎么写的？
- 请求参数为什么需要校验？
- 数据为什么要存到数据库，而不是存在变量里？
- 为什么要写测试？
- 一个后端项目为什么要分文件？
