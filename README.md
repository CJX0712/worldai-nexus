# WorldAI Nexus

<p align="center">
  <a href="https://github.com/CJX0712/worldai-nexus-0869/actions/workflows/ci.yml"><img src="https://github.com/CJX0712/worldai-nexus-0869/actions/workflows/ci.yml/badge.svg" alt="ci"></a>
  <a href="https://github.com/CJX0712/worldai-nexus-0869/releases"><img src="https://img.shields.io/github/v/release/CJX0712/worldai-nexus-0869?sort=semver" alt="release"></a>
  <a href="https://github.com/CJX0712/worldai-nexus-0869/blob/main/LICENSE"><img src="https://img.shields.io/github/license/CJX0712/worldai-nexus-0869" alt="license"></a>
  <img src="https://img.shields.io/badge/author-%E6%99%A8%E6%98%9F-1f6feb" alt="author">
</p>

> 模块化、端到端可运行的本地优先 AI 系统。复用业界领先开源成果，按单一职责划分模块，每个模块以 Protocol 定义接口、运行时注入实现，可独立验证、可协同成链。

- 作者：**晨星**
- 版本：1.0.0
- 许可：MIT

---

## 1. 特性

- **端到端可运行**：入库 → 混合检索 → 工具路由 → 大模型生成，完整链路开箱即用。
- **离线可验证**：默认注入零依赖 Mock 实现（LLM / 向量 / 嵌入全离线），无网络、无 API Key、无模型权重即可跑通整链与全部测试。
- **模块化 + 接口驱动**：各模块只依赖 `Protocol`，运行时注入实现，可独立单元测试。
- **复用而非重造**：底层复用 FastAPI / fastembed / FAISS / llama.cpp / pypdf / rank-bm25 等成熟开源组件。
- **可切换生产后端**：通过环境变量从 Mock 切换到 OpenAI 兼容服务 / 本地 GGUF / FAISS / FastEmbed，无需改代码。
- **单文件 UI**：`ui/index.html` 零依赖聊天界面，支持入库、问答、来源展示、内置评估。

---

## 2. 快速开始

### 2.1 安装（核心，轻量）

```bash
cd worldai-nexus-0869
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2.2 启动服务（默认 Mock 后端，离线）

```bash
python -m api.main
# 或
worldai-serve
```

访问 `http://localhost:8000/health` 查看状态，浏览器打开 `ui/index.html` 使用聊天界面。

### 2.3 命令行

```bash
worldai ingest --text "你的文档内容"          # 入库
worldai ask "WorldAI Nexus 是什么？"          # 问答
worldai eval                                  # 运行内置评估
worldai serve                                 # 等价于 python -m api.main
```

---

## 3. 项目结构

```
worldai-nexus/
├── core/            # 配置、日志、共享类型、Protocol 定义
├── llm/             # LLM 网关: Mock / OpenAI兼容 / llama.cpp
├── embeddings/      # 嵌入: HashEmbedder(离线) / FastEmbed
├── vectorstore/     # 向量库: 内存余弦(离线) / FAISS
├── ingestion/       # 文档加载、切分、入库流水线
├── retrieval/       # 混合检索(向量+BM25) 与 倒数排名融合重排
├── tools/           # 可插拔工具: calculator / datetime / web_search
├── agent/           # 编排中枢: 确定性路由 + RAG + 工具链
├── api/             # FastAPI 服务(仅装配)
├── cli/             # 命令行入口
├── compose.py       # 依赖注入容器(唯一布线点)
├── eval.py          # 内置评估套件
├── ui/index.html    # 单文件聊天界面
├── tests/           # 离线单元测试 + API 集成测试
├── scripts/verify.py# 自包含 E2E 验证(拉起真实服务进程)
├── docs/            # 架构 / 规格 / OpenAPI / ADR
├── requirements.txt / requirements-ai.txt / requirements.lock.txt
├── Dockerfile / docker-compose.yml
└── tools/scan_emoji.py  # P0 门禁: 全仓 emoji 扫描
```

---

## 4. HTTP API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/health`  | 健康检查，返回当前后端实现 |
| POST | `/ingest`  | 入库：请求体 `{"text": "...", "doc_id": "x"}` 或 `{"file": "path"}` |
| POST | `/chat`    | 问答：请求体 `{"query": "...", "k": 5, "use_rag": true}` |
| POST | `/search`  | 检索：请求体 `{"query": "...", "k": 5}` |
| GET  | `/tools`   | 列出已注册工具 |
| GET  | `/eval`    | 运行内置评估，返回 `{"passed": n, "total": m, "ok": bool}` |

完整定义见 `docs/openapi.yaml`。

---

## 5. 切换到生产后端

通过环境变量选择实现，零代码改动：

| 变量 | 可选值 | 说明 |
|------|--------|------|
| `WORLDAI_LLM` | `mock` / `openai` / `llamacpp` | 大模型提供方 |
| `WORLDAI_EMBEDDER` | `mock` / `fastembed` | 嵌入实现 |
| `WORLDAI_VECTORSTORE` | `memory` / `faiss` | 向量库 |
| `OPENAI_BASE_URL` | URL | OpenAI 兼容端点（Ollama/vLLM/官方） |
| `OPENAI_API_KEY` | key | API Key |
| `OPENAI_MODEL` | 模型名 | 模型标识 |
| `WORLDAI_LLAMA_MODEL` | 路径 | 本地 GGUF 模型路径 |
| `WORLDAI_EMBED_MODEL` | 模型名 | FastEmbed 模型（如 `BAAI/bge-small-en-v1.5`） |

生产后端需安装额外依赖：

```bash
pip install -r requirements-ai.txt
```

---

## 6. 可复现与验证

### 6.1 锁定依赖

- `requirements.txt`：核心运行时，钉版。
- `requirements-ai.txt`：生产 AI 后端，钉版。
- `requirements.lock.txt`：由已验证环境 `pip freeze` 生成的完整闭包，保证可安装。

### 6.2 一键验证

```bash
pytest                 # 离线单元测试 + API 集成测试
python scripts/verify.py   # 拉起真实服务进程跑端到端链路
python tools/scan_emoji.py # P0 门禁: 全仓 emoji 扫描
```

默认后端下，以上三步均可在**无网络、无 Key、无模型权重**环境中全绿。

---

## 7. Docker 部署

```bash
docker compose up --build
# 访问 http://localhost:8000
```

容器内默认使用 Mock 后端；如需语义检索 / 本地模型，请在镜像中追加 `requirements-ai.txt` 并相应设置环境变量。

---

## 8. 设计原则

1. **单一职责**：每个模块只做一件事，边界清晰。
2. **接口驱动（Protocol）**：模块间通过 Protocol 解耦，运行时注入实现。
3. **离线优先**：默认实现零外部依赖，保证可验证、可复现。
4. **复用开源**：底层能力来自成熟开源项目，不自研底层。
5. **确定性兜底**：算术等可判定任务走确定性路由，避免小模型不可靠。

详见 `docs/ARCHITECTURE.md` 与 `docs/SPEC.md`。

---

作者：晨星 ｜ 许可：MIT
