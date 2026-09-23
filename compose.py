"""WorldAI Nexus - 依赖注入容器 (Composition Root)。

按 AppConfig 选择各模块的"实现"，在运行时注入 Protocol，组装出完整可运行链路。
这是系统唯一的布线点: 其余模块只依赖 Protocol，互不直接耦合。

作者: 晨星
"""
from __future__ import annotations

from core.config import AppConfig
from agent.react import Agent
from embeddings.fastembed_ import FastEmbedEmbedder
from embeddings.mock import HashEmbedder
from llm.llama_cpp_ import LlamaCppLLM
from llm.mock import MockLLM
from llm.openai_compat import OpenAICompatLLM
from retrieval.hybrid import HybridRetriever
from tools.base import ToolRegistry
from tools.calculator import CalculatorTool
from tools.datetime_tool import DateTimeTool
from tools.web_search import WebSearchTool
from vectorstore.faiss_ import FaissVectorStore
from vectorstore.memory import InMemoryVectorStore


class Container:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

        # ---- 嵌入 (Embedder) ----
        if config.embedder == "fastembed":
            self.embedder = FastEmbedEmbedder(config.embed_model)
        else:
            self.embedder = HashEmbedder(dim=256)

        # ---- 向量库 (VectorStore) ----
        if config.vectorstore == "faiss":
            base_vs = FaissVectorStore(self.embedder.dim)
        else:
            base_vs = InMemoryVectorStore()
        self.retriever = HybridRetriever(self.embedder, base_vs)

        # ---- 大模型 (LLMProvider) ----
        if config.llm_provider == "openai":
            self.llm = OpenAICompatLLM(
                config.openai_base_url, config.openai_api_key, config.openai_model
            )
        elif config.llm_provider == "llamacpp":
            self.llm = LlamaCppLLM(config.llama_model_path)
        else:
            self.llm = MockLLM()

        # ---- 工具 (ToolRegistry) ----
        self.tools = ToolRegistry()
        self.tools.register(CalculatorTool())
        self.tools.register(DateTimeTool())
        self.tools.register(WebSearchTool())

        # ---- 编排中枢 (Agent) ----
        self.agent = Agent(self.llm, self.retriever, self.tools)

    # ---- 便捷入库入口 ----
    def ingest_text(self, text: str, doc_id: str = "mem"):
        from ingestion.pipeline import IngestionPipeline

        return IngestionPipeline(self.embedder, self.retriever).ingest_text(text, doc_id)

    def ingest_file(self, path: str):
        from ingestion.pipeline import IngestionPipeline

        return IngestionPipeline(self.embedder, self.retriever).ingest_file(path)
