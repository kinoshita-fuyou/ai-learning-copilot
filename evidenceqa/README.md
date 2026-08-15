# EvidenceQA

> 一个面向企业内部文档的可追溯知识库问答系统。

EvidenceQA 的目标不是做一个只会聊天的页面，而是让回答能回到原始资料：管理员上传制度、产品手册或操作规范，系统完成解析、检索、生成和引用溯源。项目刻意覆盖 AI 应用开发岗位常见的 RAG、后端服务、评测和部署能力。

## 状态

**已完成（v1.0.0）**：文档接入 → 切分 → 向量检索 → RAG 问答 → 评测 → Web 控制台
→ Docker 部署全链路。26 个自动化测试全绿，GitHub Actions CI 持续回归。
同仓库的补充项目 [ReportFlow Agent](../reportflow/README.md)（结构化输出 +
工具调用 + 失败降级）也已交付，20 个自动化测试全绿。十天作品集全部完成。

## 功能特性

- FastAPI 服务与自动化接口文档（`/docs`）
- Markdown / TXT 上传，扩展名、UTF-8 编码、空文件、1 MB 大小四重校验
- SQLite 持久化：文档正文、切块、embedding 分层存储，自动迁移回填
- 段落优先切分：保留 chunk 字符范围与重叠上下文，引用可精确溯源
- 本地确定性 Embedding（特征哈希 + CJK 双字元），免 API Key，接口与云端一致可替换
- 余弦相似度 Top-K 检索，返回来源文档、片段号与相关度分数
- RAG 问答 `/ask`：回答附带引用来源；支持离线模板与 OpenAI 兼容 LLM 双 Provider
- 检索评测：Recall@K、MRR、平均延迟，内置 20 道跨文档评测题
- 简洁 Web 控制台：文档库 / 问答 / 检索 / 评测四页签，纯原生前端零依赖
- Docker Compose 一键部署，命名卷持久化 + 健康检查
- 一键演示 `scripts/demo.sh`：重建演示库 → 启动 → 打开浏览器
- 面试材料：项目概述、Q&A、演示脚本、学习路径、简历条目、上线自检清单
- Pytest 测试套件 + GitHub Actions CI

## 演示与面试材料

| 文件 | 内容 |
| --- | --- |
| [data/demo_policy.md](data/demo_policy.md) | 企业制度：远程办公、报销、IT、考勤、数据安全 |
| [data/demo_product_manual.md](data/demo_product_manual.md) | 产品手册：云盘上传、共享、版本、审计 |
| [data/demo_engineering_guide.md](data/demo_engineering_guide.md) | 研发规范：分支、测试、灰度发布、应急 |
| [data/eval_set.json](data/eval_set.json) | 20 道跨文档检索评测题 |
| [interview/01-project-overview.md](interview/01-project-overview.md) | 项目概述、架构、简历描述模板 |
| [interview/02-interview-qa.md](interview/02-interview-qa.md) | 17 道面试 Q&A（含追问预案） |
| [interview/03-demo-script.md](interview/03-demo-script.md) | 5 分钟现场演示脚本 |
| [interview/04-learning-path.md](interview/04-learning-path.md) | 8 周学习路径与简历策略 |
| [interview/05-resume.md](interview/05-resume.md) | 简历条目定稿（中英双版） |
| [interview/06-launch-checklist.md](interview/06-launch-checklist.md) | 上线 / 面试自检清单 |

## 架构

```text
Document upload -> SQLite document store -> chunk pipeline -> vector retrieval
                                                        -> LLM answer + citations
```

## API

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Web 控制台（上传、问答、检索、评测） |
| GET | `/health` | 健康检查 |
| POST | `/documents/upload` | 上传 `.md` 或 `.txt` 文档 |
| GET | `/documents` | 查看文档列表 |
| GET | `/documents/{document_id}` | 查看文档元数据 |
| GET | `/documents/{document_id}/chunks` | 查看清洗后的切分结果 |
| GET | `/search?q=...&top_k=5` | 向量检索最相关 chunk，含来源与字符范围 |
| POST | `/ask` | RAG 问答，返回生成的回答与引用来源 |
| GET | `/eval/demo` | 内置演示评测集 |
| POST | `/eval/retrieval` | 检索评测：传入评测集，返回 Recall@K、MRR 与延迟 |
| DELETE | `/documents/{document_id}` | 删除文档 |

启动后访问 `http://127.0.0.1:8001` 使用 Web 控制台，或访问 `/docs` 直接试用接口。

## 配置

| 环境变量 | 默认 | 说明 |
| --- | --- | --- |
| `EVIDENCEQA_DB_PATH` | `./evidenceqa.db` | SQLite 数据库文件位置 |
| `EVIDENCEQA_ANSWER_PROVIDER` | `auto` | `template` / `llm` / `auto`；测试与演示默认强制 `template` |
| `OPENAI_API_KEY` | 无 | 设置后 `auto` 模式启用 LLM 回答 |
| `OPENAI_BASE_URL` | 无 | OpenAI 兼容 API 地址（可接中转/本地模型） |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | LLM 模型名 |

LLM 调用失败时 `/ask` 返回 502 并携带原因，不会静默返回错误答案。

## 本地运行

```bash
cd evidenceqa
./scripts/setup.sh
./scripts/start.sh
```

面试演示（重建演示库 + 启动 + 打开浏览器）：

```bash
./scripts/demo.sh
```

运行测试：

```bash
./scripts/test.sh
```

`setup.sh` 会创建虚拟环境并安装依赖；脚本内部隔离了 `PYTHONPATH`，避免误用
系统中其他 Python 环境的包（若手动创建环境，请同样使用
`env -u PYTHONPATH pip install -r requirements.txt`）。

## Docker 运行

```bash
docker compose up --build
```

启动后访问 `http://127.0.0.1:8001`。数据库存放在 Docker 命名卷 `evidenceqa-data` 中，
删除容器不会丢失数据。也可通过环境变量 `EVIDENCEQA_DB_PATH` 指定数据库文件位置。

## 项目结构

```text
evidenceqa/
├── app/                  # 后端源码
│   ├── main.py           # FastAPI 路由与启动
│   ├── chunking.py       # 清洗与切分
│   ├── embeddings.py     # 本地确定性 Embedding
│   ├── retrieval.py      # Top-K 检索
│   ├── answering.py      # 模板 / LLM 双 Provider
│   ├── evaluation.py     # Recall@K / MRR / 延迟评测
│   ├── repository.py     # SQLite 数据访问
│   └── static/           # Web 控制台（原生 HTML/CSS/JS）
├── data/                 # 演示文档与评测集
├── interview/            # 面试材料
├── scripts/              # 启动 / 测试 / 一键演示
├── tests/                # 26 个 pytest 用例
├── Dockerfile
└── docker-compose.yml
```

## 测试与 CI

```bash
./scripts/test.sh
```

- 26 个用例覆盖切分、Embedding、检索、问答、评测、错误处理与 UI
- 测试通过 `EVIDENCEQA_ANSWER_PROVIDER=template` 强制离线，与开发机环境无关
- 每次 push 由 GitHub Actions 自动回归（`.github/workflows/ci.yml`）

## 十天作品集计划

| 项目 | 复杂度 | 完成日 | 面试价值 |
| --- | --- | --- | --- |
| EvidenceQA | 主项目，8 天 | Day 8 | RAG 全链路、引用溯源、评测、部署 |
| ReportFlow Agent | 补充项目，2 天 | Day 10 | 结构化输出、工具调用、工作流与失败处理 |

十天内只做这两个项目。EvidenceQA 做到可演示、可测试、可解释；ReportFlow Agent 保持小而完整，用来证明我不仅会知识库，也能把 LLM 接进业务流程。

## 面试切入点

- 为什么先限制上传类型与大小，后续如何扩展 PDF 解析？
- 文档正文和后续 chunk、embedding 如何解耦存储？
- 检索结果为何需要引用、评测和失败兜底？
- RAG 的 chunk、召回、重排和答案生成分别如何影响质量？
