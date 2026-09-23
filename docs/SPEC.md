# SPEC - WorldAI Nexus v1.0.0

> 生成日期：2026-09-24
> 状态：已确认（基于离线可验证架构）
> 作者：晨星

---

## 1. 产品定义

- **一句话描述**：本地优先、模块化、端到端可运行的 AI 系统，复用开源成果，按单一职责划分模块并提供清晰接口。
- **目标用户**：需要在本地 / 私有环境快速搭建可运行 AI 链路（RAG + 工具 + 生成）的开发者与团队。
- **核心问题**：从零自研 AI 底层成本高、难复用；本系统以「接口 + 注入 + 复用开源」的方式，交付一个可验证、可复现、可部署的完整链路。

## 2. MVP 范围（锁定）

| 优先级 | 功能 | 验收摘要 |
|--------|------|----------|
| P0 | 文档入库（txt/md/pdf） | 加载→切分→嵌入→写入向量库 |
| P0 | 混合检索（向量+BM25，RRF 融合） | 给定查询返回 Top-K 片段 |
| P0 | Agent 编排（路由+RAG+LLM） | 返回答案 + 来源 + 工具调用 |
| P0 | 确定性算术路由 | 算术表达式交由 calculator，结果正确 |
| P0 | HTTP API（health/ingest/chat/search/eval/tools） | 端点可用且返回结构正确 |
| P0 | CLI（ingest/ask/eval/serve） | 命令可用 |
| P0 | 单文件 UI 聊天界面 | 可入库、可问答、展示来源 |
| P1 | 生产后端切换（OpenAI兼容 / llama.cpp / FAISS / FastEmbed） | 环境变量切换，无需改代码 |
| P1 | 内置评估套件 | `/eval` 与 CLI 均返回通过率 |

## 3. 明确不做（Out-of-Scope）

| 不做 | 原因 | 何时考虑 |
|------|------|----------|
| 自研向量库 / 自研嵌入模型 | 已有 FAISS / fastembed 等成熟开源 | 无 |
| 多租户 / 权限系统 | MVP 聚焦单用户本地链路 | v2.0 |
| 模型微调 | 超出可复现交付范围 | 有需求后 |
| 实时流式输出 | Mock 后端为确定性文本 | 接真实 LLM 后启用 |

## 4. 技术架构（锁定）

| 层 | 技术（默认 / 生产） |
|----|------|
| API | FastAPI（仅装配） |
| LLM | MockLLM / OpenAI 兼容 / llama.cpp |
| 嵌入 | HashEmbedder / FastEmbed |
| 向量库 | 内存余弦 / FAISS |
| 检索 | 向量 + BM25 + RRF |
| 服务 | uvicorn |
| 配置 | 环境变量驱动的依赖注入 |

## 5. API 端点清单（锁定）

| Method | Path | 功能 | 认证 | 请求体 | 响应 |
|--------|------|------|------|--------|------|
| GET | /health | 健康检查 | 否 | - | `{status, llm, embedder, vectorstore}` |
| POST | /ingest | 入库 | 否 | `{text?, doc_id?, file?}` | `{chunks}` |
| POST | /chat | 问答 | 否 | `{query, k?, use_rag?}` | `{answer, model, sources, tool_calls}` |
| POST | /search | 检索 | 否 | `{query, k?}` | `{hits}` |
| GET | /tools | 工具列表 | 否 | - | `{tools}` |
| GET | /eval | 评估 | 否 | - | `{passed, total, ok}` |

## 6. 数据库表清单

无持久化数据库。检索状态存于进程内向量库 / BM25 索引（可替换为 FAISS 持久化）。

## 7. 页面清单

| 页面 | 路由 | 说明 |
|------|------|------|
| 聊天界面 | `ui/index.html` | 单文件，调用 /ingest、/chat、/search、/eval |

## 8. 设计 Token（UI）

- 主色：`#2f5fe0`（蓝）
- 背景：`#f6f8fb`，面板：`#ffffff`
- 文本：`#1f2933` / 次要 `#6b7785`
- 图标：内联 SVG（禁止 emoji）
- 主题：浅色

## 9. 验收标准（EARS）

| 编号 | 功能 | 验收标准 |
|------|------|----------|
| AC-01 | 入库 | When 提交合法文本，系统**必须**返回 chunk 数 ≥ 1 |
| AC-02 | 算术路由 | If 输入为纯算术表达式，系统**必须**返回正确计算结果 |
| AC-03 | RAG 问答 | When 查询命中已入库知识，系统**必须**返回含来源的答案 |
| AC-04 | 检索 | When 查询含关键词，系统**必须**返回 ≥1 条相关片段 |
| AC-05 | 评估 | When 调用 /eval，系统**必须**返回 ok=true（默认后端） |
| AC-06 | 错误流 | If 入库缺体，系统**必须**返回 400 |

## 10. 边界与约束

- 默认后端纯离线，无网络依赖。
- 向量库为进程内存，重启后需重新入库（FAISS 持久化为后续增强）。
- 单文件 ≤ 300 行，入口仅装配。

## 11. 内嵌已知坑（已规避）

| 坑 | 根因 | 修法 |
|----|------|------|
| BM25 极小语料排序反转 | rank_bm25 idf 可为负 | 自实现恒非负 idf |
| localhost 被代理劫持 | httpx trust_env 默认 True | 指向localhost的Client 一律 trust_env=False |
| emoji 误作功能图标 | P0 规则 | 全仓扫描门禁，改用 SVG |

## 12. 端到端验证步骤

```bash
pip install -r requirements.txt
pytest                                  # 离线单测全绿
python scripts/verify.py                 # 真实服务进程端到端全绿
python -m api.main &                     # 启动服务
curl -X POST localhost:8000/ingest -H 'Content-Type: application/json' -d '{"text":"WorldAI Nexus 是晨星打造的模块化 AI 系统。","doc_id":"t"}'
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{"query":"WorldAI Nexus 是什么？"}'
```
