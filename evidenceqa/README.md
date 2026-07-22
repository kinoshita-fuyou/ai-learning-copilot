# EvidenceQA

> 一个面向企业内部文档的可追溯知识库问答系统。

EvidenceQA 的目标不是做一个只会聊天的页面，而是让回答能回到原始资料：管理员上传制度、产品手册或操作规范，系统完成解析、检索、生成和引用溯源。项目刻意覆盖 AI 应用开发岗位常见的 RAG、后端服务、评测和部署能力。

## 当前进度

### 已完成：文档接入层

- FastAPI 服务与自动化接口文档
- Markdown / TXT 上传，UTF-8 编码、空文件、文件类型与 1 MB 大小校验
- SQLite 文档元数据与正文持久化
- 文档列表、详情查询、删除接口
- Pytest 接口测试

### 即将完成

1. 文本清洗与语义切分
2. Embedding、向量索引与混合检索
3. 带来源引用的 RAG 问答
4. 检索评测集、延迟和质量指标
5. 简洁 Web 控制台、Docker 与演示数据

## 架构

```text
Document upload -> SQLite document store -> chunk pipeline -> vector retrieval
                                                        -> LLM answer + citations
```

## API

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/documents/upload` | 上传 `.md` 或 `.txt` 文档 |
| GET | `/documents` | 查看文档列表 |
| GET | `/documents/{document_id}` | 查看文档元数据 |
| DELETE | `/documents/{document_id}` | 删除文档 |

启动后可访问 `http://127.0.0.1:8001/docs` 直接试用接口。

## 本地运行

```bash
cd evidenceqa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/start.sh
```

运行测试：

```bash
./scripts/test.sh
```

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
