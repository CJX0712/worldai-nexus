"""WorldAI Nexus - Retrieval 模块: 混合检索 (向量 + BM25)。

HybridRetriever 同时满足 VectorStore 协议 (add) 与 Retriever 协议 (search)，
内部维护向量库 + BM25 关键词索引，查询时对二者做倒数排名融合。
BM25 使用恒非负的 Robertson idf 公式，规避 rank_bm25 在极小语料下 idf 为负、排序反转的已知坑。

作者: 晨星
"""
from __future__ import annotations

import math
import re

from core.types import SearchHit
from embeddings.mock import _tokens
from retrieval.rerank import reciprocal_rank_fusion

_ASCII_RE = re.compile(r"[a-zA-Z0-9]+")


class _Bm25Index:
    """极简 BM25 索引 (chunk_id -> 分词)，恒非负 idf。"""

    def __init__(self, docs: list[tuple[str, str]]) -> None:
        self.records = [(cid, _tokens(text)) for cid, text in docs]
        self.n = len(self.records)
        self.df: dict[str, int] = {}
        self.tf: list[dict[str, int]] = []
        self.doc_len: list[int] = []
        for _, toks in self.records:
            self.doc_len.append(len(toks))
            f: dict[str, int] = {}
            for t in toks:
                f[t] = f.get(t, 0) + 1
            self.tf.append(f)
            for t in f:
                self.df[t] = self.df.get(t, 0) + 1
        self.avgdl = (sum(self.doc_len) / self.n) if self.n else 0.0

    def _idf(self, term: str) -> float:
        n = self.df.get(term, 0)
        return math.log(1.0 + (self.n - n + 0.5) / (n + 0.5))

    def search(self, query: str, top_k: int = 10) -> list[SearchHit]:
        if self.n == 0:
            return []
        qtokens = _tokens(query)
        scores: list[tuple[float, str]] = []
        for i, (cid, _) in enumerate(self.records):
            dl = self.doc_len[i] if self.doc_len[i] else 1
            norm_dl = dl / self.avgdl if self.avgdl else 1.0
            score = 0.0
            for t in set(qtokens):
                if t not in self.df:
                    continue
                tf = self.tf[i].get(t, 0)
                idf = self._idf(t)
                score += idf * (tf * (1.2 + 1)) / (tf + 1.2 * (1 - 0.75 + 0.75 * norm_dl))
            scores.append((score, cid))
        scores.sort(reverse=True)
        return [SearchHit(chunk_id=cid, doc_id="", text="", score=float(s)) for s, cid in scores[:top_k]]


class HybridRetriever:
    """混合检索器: 向量语义 + BM25 关键词，倒数排名融合。"""

    def __init__(self, embedder, vectorstore) -> None:
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.corpus: list[tuple[str, str, str, dict]] = []  # (chunk_id, doc_id, text, meta)
        self._by_id: dict[str, tuple[str, str, str, dict]] = {}
        self._bm25 = _Bm25Index([])

    # ---- VectorStore 协议: 入库 ----
    def add(self, vectors: list[list[float]], docs: list[str], metas: list[dict] | None = None) -> None:
        metas = metas or [{} for _ in docs]
        self.vectorstore.add(vectors, docs, metas)
        for d, m in zip(docs, metas):
            cid = m.get("chunk_id", "")
            did = m.get("doc_id", "")
            self.corpus.append((cid, did, d, m))
            self._by_id[cid] = (cid, did, d, m)
        self._bm25 = _Bm25Index([(c[0], c[2]) for c in self.corpus])

    # ---- Retriever 协议: 查询 ----
    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        qv = self.embedder.embed([query])[0]
        vhits = self.vectorstore.search(qv, k=max(k * 3, 10))
        bhits = self._bm25.search(query, top_k=max(k * 3, 10))
        fused = reciprocal_rank_fusion(vhits, bhits)
        out: list[SearchHit] = []
        for h in fused[:k]:
            rec = self._by_id.get(h.chunk_id)
            if rec is None:
                continue
            out.append(
                SearchHit(
                    chunk_id=rec[0],
                    doc_id=rec[1],
                    text=rec[2],
                    score=h.score,
                    meta=rec[3],
                )
            )
        return out
