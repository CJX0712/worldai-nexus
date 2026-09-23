"""WorldAI Nexus - 模块协议 (Protocol) 定义。

所有模块仅依赖这些 Protocol，运行时注入具体实现，从而可独立验证、可协同成链。

作者: 晨星
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.types import ChatMessage, SearchHit


@runtime_checkable
class LLMProvider(Protocol):
    """大模型推理提供方。"""
    name: str

    def complete(self, prompt: str, **kwargs) -> str: ...

    def chat(self, messages: list[ChatMessage], **kwargs) -> str: ...


@runtime_checkable
class Embedder(Protocol):
    """文本向量化提供方。"""
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


@runtime_checkable
class VectorStore(Protocol):
    """向量存储与语义检索。"""
    def add(self, vectors: list[list[float]], docs: list[str], metas: list[dict] | None = None) -> None: ...

    def search(self, query_vec: list[float], k: int = 5) -> list[SearchHit]: ...


@runtime_checkable
class Retriever(Protocol):
    """面向查询文本的检索器 (语义 + 关键词混合)。"""
    def search(self, query: str, k: int = 5) -> list[SearchHit]: ...


@runtime_checkable
class Tool(Protocol):
    """可插拔工具。"""
    name: str
    description: str

    def run(self, **kwargs) -> str: ...
