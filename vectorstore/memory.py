"""WorldAI Nexus - VectorStore 模块: 内存余弦实现 (离线)。

进程内向量存储，使用余弦相似度检索。无任何外部依赖。

作者: 晨星
"""
from __future__ import annotations

from core.types import SearchHit
from vectorstore.base import cosine


class InMemoryVectorStore:
    """内存向量存储 (离线)。"""
    def __init__(self) -> None:
        self._vecs: list[list[float]] = []
        self._docs: list[tuple[str, dict]] = []

    def add(self, vectors: list[list[float]], docs: list[str], metas: list[dict] | None = None) -> None:
        metas = metas or [{} for _ in docs]
        for v, d, m in zip(vectors, docs, metas):
            self._vecs.append(v)
            self._docs.append((d, m))

    def search(self, query_vec: list[float], k: int = 5) -> list[SearchHit]:
        scored = []
        for i, v in enumerate(self._vecs):
            s = cosine(query_vec, v)
            d, m = self._docs[i]
            scored.append((s, i, d, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        hits: list[SearchHit] = []
        for s, i, d, m in scored[:k]:
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
