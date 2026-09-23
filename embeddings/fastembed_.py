"""WorldAI Nexus - Embeddings 模块: FastEmbed 生产实现。

基于 ONNX 的轻量嵌入模型 (默认 BAAI/bge-small)，首次使用自动下载权重。
仅在 embedder=fastembed 时加载。

作者: 晨星
"""
from __future__ import annotations

from core.errors import ProviderError


class FastEmbedEmbedder:
    """FastEmbed 嵌入器 (生产级语义向量)。"""
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:  # pragma: no cover
            raise ProviderError("未安装 fastembed，请执行 pip install fastembed") from exc
        self._model = TextEmbedding(model_name=model_name)
        probe = list(self._model.embed(["probe"]))
        self.dim = len(probe[0])

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [list(v) for v in self._model.embed(texts)]
