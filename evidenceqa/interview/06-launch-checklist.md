# EvidenceQA 上线 / 面试自检清单

> 面试前 24 小时按顺序过一遍，每项都能打勾再出门。

## 代码与测试

- [ ] `pytest -q` 全绿（当前 32 个用例）
- [ ] `git status` 干净，最新代码已 push
- [ ] GitHub Actions 上最后一次 CI 通过
- [ ] 本地与 CI 的测试数一致（环境无关，靠 `EVIDENCEQA_ANSWER_PROVIDER=template` 隔离）

## 本地演示

- [ ] `./scripts/demo.sh` 一次跑通：重建演示库 → 启动 → 浏览器打开
- [ ] 断网状态下也能跑（全程离线：本地 Embedding + 模板回答）
- [ ] 文档库显示 3 份文档，删除/重传正常
- [ ] 问答页：问"远程办公需要提前多久申请"有回答 + 引用来源
- [ ] 检索页：问"P0 故障多久内响应"命中研发规范文档；`hybrid=false` 可对比纯向量
- [ ] 评测页：一键运行，混合检索 Recall@K=1.0、MRR=1.0（纯向量基线 MRR=0.9683）
- [ ] `/docs` 接口文档可打开

## Docker 部署

- [ ] `docker compose up --build` 启动成功
- [ ] `http://127.0.0.1:8001/health` 返回 ok
- [ ] 重启容器后数据仍在（命名卷持久化）
- [ ] 生产配置说明：`EVIDENCEQA_DB_PATH`、`EVIDENCEQA_ANSWER_PROVIDER`、`OPENAI_API_KEY`

## 面试材料

- [ ] 简历条目（05-resume.md）数字与仓库一致
- [ ] 面试 Q&A（02）完整过一遍，能用自己的话讲
- [ ] 5 分钟演示脚本（03）演练至少 2 遍并计时
- [ ] 学习路径（04）的下一步计划能讲清楚
- [ ] 被问"还能怎么改进"时有答案（Q17 优先级）

## 已知边界（主动讲比被问好）

- 特征哈希 Embedding 是词袋级别，不懂语义；换真实 Embedding 需重跑评测
- 检索是全表扫描，百万级 chunk 需换向量索引（FAISS / sqlite-vec / pgvector）
- 评测只覆盖检索，不覆盖回答质量；生产需加引用忠实度评测
- 无鉴权与多租户隔离，生产需补 API Key + 文档级权限
- 只支持 md/txt，PDF/Word 需加解析器（管线已预留）
