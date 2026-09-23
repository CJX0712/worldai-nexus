# WorldAI Nexus - 系统架构

> 作者：晨星 ｜ 版本：1.0.0

## 1. 设计原则

| 原则 | 落地点 |
|------|--------|
| 单一职责 | 每个包只解决一类问题（嵌入 / 检索 / 工具 / 编排 …） |
| 接口驱动 | 模块间只依赖 `core/protocols.py` 中的 Protocol，互不直接耦合 |
| 运行时注入 | `compose.py` 是唯一的布线点，按配置选择实现 |
| 离线优先 | 默认实现零外部依赖，无网络 / Key / 权重即可验证 |
| 复用开源 | 底层复用 FastAPI / fastembed / FAISS / llama.cpp / pypdf / rank-bm25 |

## 2. 模块拓扑与调用关系

```
                ┌──────────────┐
   用户/UI ───▶ │   api (HTTP) │  (仅装配, 零业务)
                └──────┬───────┘
                       │ 委托
                ┌──────▼───────┐
                │   agent       │  编排中枢
                └───┬──────┬────┘
         路由/工具   │      │  RAG
      ┌─────────────┘      └─────────────┐
      ▼                                  ▼
┌──────────┐                   ┌──────────────────┐
│ tools     │                   │  retrieval        │ 混合检索
│ (Registry)│                   │  (vector + BM25)   │
└──────────┘                   └──┬────────────┬────┘
                                  ▼            ▼
                           ┌──────────┐  ┌──────────────┐
                           │embeddings│  │ vectorstore   │
                           └──────────┘  └──────────────┘
                                  ▲            ▲
                                  └─ ingestion 管线 ─┘
                                        (load→chunk→embed→store)
        llm 提供方 (mock / openai / llamacpp) 被 agent 直接调用
```

## 3. 核心接口（Protocol）

定义在 `core/protocols.py`，是模块间唯一的契约：

- `LLMProvider`：`complete(prompt)` / `chat(messages)`
- `Embedder`：`embed(texts) -> list[list[float]]`，含 `dim`
- `VectorStore`：`add(vectors, docs, metas)` / `search(query_vec, k)`
- `Retriever`：`search(query, k) -> list[SearchHit]`
- `Tool`：`name` / `description` / `run(**kwargs)`

任何模块都可以用任意实现替换，只要满足 Protocol —— 这正是「可独立验证」的基础：测试时用 Mock 注入，生产时用真实后端。

## 4. 数据流：一次问答

1. `api` 收到 `/chat`，委托 `agent.run(query)`。
2. `agent.router` 先做**确定性路由**：纯算术表达式（如 `12*(3+4)`）直接交给 `calculator` 工具，返回结果，跳过 LLM，避免小模型算术不可靠。
3. 非算术请求进入 RAG 路径：`retriever.search(query)` 做**混合检索**。
4. 混合检索 = 向量语义检索 + BM25 关键词检索，二者用**倒数排名融合 (RRF)** 合并，召回 Top-K 片段。
5. `agent` 用 `<kb-context>` 包裹召回内容，拼成提示词交给 `LLMProvider.complete()`。
6. 返回 `AgentResult`（答案 + 来源 + 工具调用记录）。

## 5. 混合检索的实现要点

- **向量检索**：`Embedder` 将查询与文档片段向量化，`VectorStore` 做余弦 / 内积检索。
- **BM25 关键词检索**：自实现 `_Bm25Index`，使用**恒非负 Robertson idf** `ln(1 + (N-n+0.5)/(n+0.5))`，规避 `rank_bm25` 在极小语料下 idf 为负导致排序反转的已知坑。
- **融合**：`reciprocal_rank_fusion` 以 `1/(rank+60)` 累加两套排名，按总分降序输出。

## 6. 配置与可切换矩阵

| 关注点 | Mock（默认） | 生产实现 | 切换方式 |
|--------|--------------|----------|----------|
| LLM | `MockLLM` | `OpenAICompatLLM` / `LlamaCppLLM` | `WORLDAI_LLM` |
| 嵌入 | `HashEmbedder` | `FastEmbedEmbedder` | `WORLDAI_EMBEDDER` |
| 向量库 | `InMemoryVectorStore` | `FaissVectorStore` | `WORLDAI_VECTORSTORE` |

## 7. 可复现与质量门禁

- 锁定依赖：`requirements.txt`（核心）+ `requirements-ai.txt`（AI 后端）+ `requirements.lock.txt`（完整闭包）。
- 验证三件套（默认后端下全部离线全绿）：
  1. `pytest` —— 26 项离线单测 + API 集成测试。
  2. `python scripts/verify.py` —— 拉起真实 HTTP 服务进程跑端到端链路。
  3. `python tools/scan_emoji.py` —— P0 门禁，禁止 emoji 作功能图标。
- 单文件 ≤ 300 行，入口仅装配零业务；模块只依赖 Protocol，运行时注入。
