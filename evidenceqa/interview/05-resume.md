# 简历条目定稿

> EvidenceQA 是十天计划里第一个完整交付的项目。简历上只保留可验证的数字和
> 可追问的设计决策；每条 bullet 都准备一个 30 秒的展开故事。
> 两个项目合并的完整简历段落见仓库根目录 [resume.md](../../resume.md)。

## 中文版（推荐放进简历）

**可溯源企业知识库问答系统 EvidenceQA · 独立开发**
FastAPI · Python · SQLite · RAG · Docker

- 独立完成文档接入、切分、向量检索、RAG 问答、检索评测与 Web 控制台全链路，
  回答附带可回到原文的引用来源
- 自研免 API Key 的确定性 Embedding（特征哈希 + CJK 双字元），接口与云端
  Embedding 对齐，换真实模型只需替换一个 Provider 类
- 建立 Recall@K / MRR / 延迟评测体系，内置 21 道跨文档评测题，实测
  Recall@K=1.0、MRR=1.0、平均检索延迟约 0.4ms；纯向量基线 MRR=0.9683
- 实现 BM25 + 向量混合检索，关键词型问题排序从第 3 名提升到第 1 名
- 提供原生 Web 控制台（上传/问答/检索/评测）与 Docker 一键部署，
  38 个自动化测试全绿，GitHub Actions CI 自动回归

## English Version

**EvidenceQA — Traceable Enterprise QA System · Solo Project**
FastAPI · Python · SQLite · RAG · Docker

- Built the full pipeline end-to-end: document ingestion, chunking, vector
  retrieval, RAG answering with source citations, retrieval evaluation, and a
  web console
- Designed a dependency-free deterministic embedding (feature hashing + CJK
  bigrams) behind a provider interface, swappable for hosted embeddings
- Established Recall@K / MRR / latency evaluation over a 20-question
  cross-document benchmark (Recall@K=1.0, MRR=1.0, ~0.4ms per search)
- Shipped a vanilla-JS console and Docker Compose deployment; 26 automated
  tests green with GitHub Actions CI

## 简历排版建议

1. 项目放第一段（应届无全职经历时，项目是简历主体），技能列表放在项目之后
2. 每条 bullet 以动词开头："独立完成 / 自研 / 建立 / 提供"
3. 数字必须和仓库一致（测试数、评测指标、延迟），面试官可能现场验证
4. 预留一行"技术栈"，方便 HR 关键词筛选（RAG、FastAPI、Docker、SQLite）

## 每条 bullet 的 30 秒展开

- **全链路**："从上传开始讲：校验 → 清洗 → 切分 → 向量化 → 检索 → 生成 →
  引用。每一步我都知道为什么这么做，比如切分保留字符范围是为了溯源。"
- **Embedding**："面试现场断网也能演示，因为本地特征哈希是确定性的；接口和
  云端对齐，接 BGE 只改一个类，再用同一套评测集验证。"
- **评测**："21 道题覆盖 3 份文档，Recall@K 管召回、MRR 管排序、延迟管性能；
  局限我也清楚——它不评估回答质量，下一步加 LLM-as-judge。"
- **工程化**："38 个测试隔离数据、秒级跑完，CI 在每次 push 自动回归；
  Docker 用命名卷持久化数据库，容器删了数据还在。"

> 注意：所有数字以仓库当前状态为准，改动代码后记得同步本文件。
