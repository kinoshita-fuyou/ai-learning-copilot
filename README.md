# AI Learning Copilot

> 十天作品集：两个可演示、可测试、可解释的 AI 应用项目。

这个仓库是学习 AI 应用开发的完整交付物，覆盖两条主线：**RAG 知识库全链路**
（EvidenceQA）与 **Agent 工作流**（ReportFlow）。两个项目都坚持同样的工程原则：
接口与实现分离、离线可演示、测试隔离环境、量化可验证。

![CI](https://github.com/kinoshita-fuyou/ai-learning-copilot/actions/workflows/ci.yml/badge.svg)

[MIT License](LICENSE)

## 项目一览

| 项目 | 定位 | 关键能力 | 验证 |
| --- | --- | --- | --- |
| [EvidenceQA](evidenceqa/README.md) | 可溯源企业知识库问答 | 文档接入、切分、Embedding、BM25 混合检索、RAG 引用溯源、Recall@K/MRR 评测、Web 控制台、Docker、可选鉴权 | 38 测试 · 21 道评测题 混合检索 MRR=1.0 |
| [ReportFlow](reportflow/README.md) | 结构化报告 Agent | 工具调用循环、结构化输出校验重试、失败降级、LLM/规则双实现 | 20 测试 · 失败注入演示 |

## 快速体验

```bash
# EvidenceQA：重建演示库 → 启动 → 打开浏览器（端口 8001）
cd evidenceqa && ./scripts/demo.sh

# ReportFlow：启动 + 示例请求 + 打开接口文档（端口 8002）
cd reportflow && ./scripts/demo.sh
```

两个项目都支持离线运行：Embedding 与报告生成有确定性本地实现，演示不依赖
网络与 API Key；配置好 `OPENAI_API_KEY` 后自动切换到真实模型。

## 测试与 CI

```bash
./check.sh                            # 一键跑两个项目（58 个用例）
```

GitHub Actions 在每次 push 时对两个项目并行回归（`.github/workflows/ci.yml`），
测试通过环境变量强制离线，结果与开发机环境无关。

首次拉取代码后，每个项目执行 `./scripts/setup.sh` 即可完成环境准备。

## 简历与面试材料

- [简历（项目经历合并版）](resume.md)
- [面试冲刺包](interview-sprint.md)（技术/行为面模拟题、反问清单、投递话术、
  面试前一周每日计划）
- [EvidenceQA 面试材料](evidenceqa/interview/)（概述、Q&A、演示脚本、学习路径、
  简历条目、自检清单）

## 目录结构

```text
.
├── evidenceqa/     # 主项目：RAG 知识库问答（Day 1-8）
├── reportflow/     # 补充项目：结构化报告 Agent（Day 9-10）
└── first_week_backend/  # 早期练习（不在作品集范围）
```
