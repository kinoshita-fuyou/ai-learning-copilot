# 简历（作品集项目经历合并版）

> 使用说明：把下方内容按顺序粘贴进简历，替换 `【】` 里的占位信息。
> 所有数字与仓库当前状态一致，改动代码后记得同步。

## 基本信息

【姓名】 · 【电话】 · 【邮箱】 · 【城市】

## 求职意向

AI 应用开发工程师 / 后端开发工程师（可实习）

## 技能清单

- **语言**：Python（类型注解、协议抽象、pytest），基础 SQL
- **Web 服务**：FastAPI、RESTful 接口设计、Pydantic 校验、错误码体系
- **AI 应用**：RAG 全链路（文档解析、切分、Embedding、BM25+向量混合检索、
  引用溯源）、工具调用 Agent、结构化输出、检索评测（Recall@K / MRR）
- **数据与存储**：SQLite（表设计、迁移回填）、JSON Schema、向量相似度
- **工程化**：Docker Compose、GitHub Actions CI、Git 工作流、自动化测试

## 项目经历

### 可溯源企业知识库问答系统 EvidenceQA · 独立开发
FastAPI · Python · SQLite · RAG · Docker

- 独立完成文档接入、切分、向量检索、RAG 问答、检索评测与 Web 控制台全链路，
  回答附带可回到原文的引用来源
- 自研免 API Key 的确定性 Embedding（特征哈希 + CJK 双字元），接口与云端
  Embedding 对齐，换真实模型只需替换一个 Provider 类
- 建立 Recall@K / MRR / 延迟评测体系，内置 21 道跨文档评测题，实测
  Recall@K=1.0、MRR=1.0、平均检索延迟约 0.4ms；纯向量基线 MRR=0.9683
- 实现 BM25 + 向量混合检索，关键词型问题排序从第 3 名提升到第 1 名
- 提供原生 Web 控制台（上传/问答/检索/评测）与 Docker 一键部署，
  32 个自动化测试全绿，GitHub Actions CI 自动回归

### 结构化报告 Agent ReportFlow · 独立开发
FastAPI · Python · OpenAI 兼容 API · 工具调用 · 失败降级

- 实现"自然语言任务 → 结构化报告"的 Agent 流水线：规划 → 工具调用 → 校验 →
  生成，LLM 与规则两套实现共用同一接口，离线可完整演示
- 工具调用循环：模型自主选择 `query_sales` / `query_tasks` / `query_incidents`
  等工具并观察结果，最终通过强制 `generate_report` 工具提交 Pydantic 校验的
  结构化输出，校验失败自动回传模型重试
- 工作流失败处理：工具失败重试一次、依赖缺失记录原因、生成异常自动降级到
  规则代理，请求永不崩溃（`degraded` / `fallback` 标记可观测）
- 20 个自动化测试覆盖工具契约、任务分类、降级与接口；CI 与 EvidenceQA 并行回归

## 项目亮点（一句话总结）

两个项目合起来证明一件事：我不仅会搭 RAG 知识库（检索质量可量化、引用可溯源），
也能把 LLM 接进业务流程（工具调用、结构化输出、失败兜底），并且全程可离线演示、
可测试、可部署。

## 一页简历排版建议

1. 技能清单压到 4 行以内，关键词对齐 JD（RAG、FastAPI、Docker 等）
2. 两个项目各 4 条 bullet，每条以动词开头、带数字
3. 教育经历放项目之后一行即可（学校、专业、毕业时间）
4. 面试前过一遍 [EvidenceQA 面试 Q&A](evidenceqa/interview/02-interview-qa.md)
   和 [上线自检清单](evidenceqa/interview/06-launch-checklist.md)

---

## English Summary (for English resumes)

**EvidenceQA — Traceable Enterprise QA System · Solo**
FastAPI · Python · SQLite · RAG · Docker

- Full pipeline: ingestion, chunking, vector retrieval, RAG answering with
  source citations, retrieval evaluation, and a web console
- Dependency-free deterministic embedding behind a provider interface,
  swappable for hosted embeddings
- 21-question cross-document benchmark with BM25+vector hybrid retrieval:
  Recall@K=1.0, MRR=1.0 (vs 0.9683 vector-only), ~0.4ms/search;
  32 tests green, GitHub Actions CI

**ReportFlow — Structured Report Agent · Solo**
FastAPI · Python · Tool Calling · Failure Handling

- Task-to-structured-report agent: plan → tool call → validate → generate,
  with offline rule agent sharing one interface with the LLM agent
- Real tool-calling loop with Pydantic-validated structured output and
  validation-retry; failed tools degrade gracefully instead of crashing
- 20 tests green, CI alongside EvidenceQA
