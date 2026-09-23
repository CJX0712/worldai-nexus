"""WorldAI Nexus - VectorStore 模块: FAISS 生产实现。

使用 faiss-cpu 的 IndexFlatIP (内积 = 归一化后的余弦) 做高性能向量检索。
仅在 vectorstore=faiss 时加载。

作者: 晨星
"""
from __future__ import annotations

import numpy as np

from core.errors import ProviderError
from core.types import SearchHit


class FaissVectorStore:
    """FAISS 向量存储 (生产级高性能)。"""
    def __init__(self, dim: int) -> None:
        try:
            import faiss
        except ImportError as exc:  # pragma: no cover
            raise ProviderError("未安装 faiss-cpu，请执行 pip install faiss-cpu") from exc
        self.dim = dim
        self._faiss = faiss
        self.index = faiss.IndexFlatIP(dim)
        self._docs: list[tuple[str, dict]] = []

    def add(self, vectors: list[list[float]], docs: list[str], metas: list[dict] | None = None) -> None:
        metas = metas or [{} for _ in docs]
        arr = np.asarray(vectors, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        arr = arr / norms
        self.index.add(arr)
        for d, m in zip(docs, metas):
            self._docs.append((d, m))

    def search(self, query_vec: list[float], k: int = 5) -> list[SearchHit]:
        k = min(k, len(self._docs))
        if k == 0:
            return []
        q = np.asarray([query_vec], dtype="float32")
        n = np.linalg.norm(q)
        if n == 0:
            n = 1.0
        q = q / n
        scores, idx = self.index.search(q, k)
        hits: list[SearchHit] = []
        for s, i in zip(scores[0], idx[0]):
            if i < 0:
                continue
            d, m = self._docs[i]
            hits.append(
                SearchHit(
                    chunk_id=m.get("chunk_id", str(i)),
                    doc_id=m.get("doc_id", str(i)),
                    text=d,
                    score=float(s),
                    meta=m,
                )
            )
        return hits
