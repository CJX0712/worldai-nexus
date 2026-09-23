"""WorldAI Nexus - Retrieval 模块: 轻量重排 (倒数排名融合)。

提供 Reciprocal Rank Fusion (RRF)，将向量检索与关键词检索的排名融合为单一排序。

作者: 晨星
"""
from __future__ import annotations

from core.types import SearchHit


def reciprocal_rank_fusion(
    vector_hits: list[SearchHit],
    bm25_hits: list[SearchHit],
    k_const: int = 60,
) -> list[SearchHit]:
    """按 chunk_id 融合两套排名，分数 = 1/(rank+k) 之和，降序返回。"""
    fused: dict[str, dict] = {}
    for rank, h in enumerate(vector_hits):
        rec = fused.setdefault(
            h.chunk_id, {"doc_id": h.doc_id, "text": h.text, "meta": h.meta, "score": 0.0}
        )
        rec["score"] += 1.0 / (rank + k_const)
    for rank, h in enumerate(bm25_hits):
        rec = fused.setdefault(
            h.chunk_id, {"doc_id": h.doc_id, "text": h.text, "meta": h.meta, "score": 0.0}
        )
        rec["score"] += 1.0 / (rank + k_const)
    ordered = sorted(fused.items(), key=lambda kv: kv[1]["score"], reverse=True)
    return [
        SearchHit(
            chunk_id=cid,
            doc_id=rec["doc_id"],
            text=rec["text"],
            score=float(rec["score"]),
            meta=rec["meta"],
        )
        for cid, rec in ordered
    ]
