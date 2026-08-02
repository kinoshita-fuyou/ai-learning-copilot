# EvidenceQA

> 一个面向企业内部文档的可追溯知识库问答系统。

EvidenceQA 的目标不是做一个只会聊天的页面，而是让回答能回到原始资料：管理员上传制度、产品手册或操作规范，系统完成解析、检索、生成和引用溯源。项目刻意覆盖 AI 应用开发岗位常见的 RAG、后端服务、评测和部署能力。

## 当前进度

### 已完成：文档接入、切分、检索、RAG 问答、评测与 Web 控制台

- FastAPI 服务与自动化接口文档
- Markdown / TXT 上传，UTF-8 编码、空文件、文件类型与 1 MB 大小校验
- SQLite 文档元数据与正文持久化
- 文档列表、详情查询、删除接口
- 段落优先的文本清洗与切分，保留 chunk 字符范围和重叠上下文
- Chunk 预览接口，便于排查后续检索效果
- 本地确定性 Embedding（特征哈希，免 API Key，接口与云端 Embedding 一致可替换）
- 余弦相似度 Top-K 检索接口 `/search`，返回 chunk 来源与字符范围
- RAG 问答接口 `/ask`：检索相关 chunk 后生成带引用来源的回答
- 检索评测模块：Recall@K、MRR、延迟测量，支持自定义评测集
- 支持本地模板回答与 OpenAI 兼容 LLM（通过环境变量切换）
- 简洁 Web 控制台：文档上传、问答、检索、评测四合一界面，开箱即用
- Docker 部署：单命令启动，数据目录可持久化
- 演示语料：3 份跨领域文档 + 20 道评测题，覆盖多文档检索场景
- 一键演示：`scripts/demo.sh` 重建演示库并启动服务
- 面试材料：项目概述、面试 Q&A、5 分钟演示脚本、学习路径
- Pytest 接口测试

### 即将完成

1. EvidenceQA 最终收尾（README 终稿、简历条目、自检清单）
2. ReportFlow Agent（Day 9-10 补充项目）

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

## 本地运行

```bash
cd evidenceqa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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

## Docker 运行

```bash
docker compose up --build
```

启动后访问 `http://127.0.0.1:8001`。数据库存放在 Docker 命名卷 `evidenceqa-data` 中，
删除容器不会丢失数据。也可通过环境变量 `EVIDENCEQA_DB_PATH` 指定数据库文件位置。

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
