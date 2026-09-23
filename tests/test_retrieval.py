"""离线单元测试: 混合检索 (向量 + BM25 倒数排名融合)。"""
from embeddings.mock import HashEmbedder
from retrieval.hybrid import HybridRetriever
from vectorstore.memory import InMemoryVectorStore


def _retriever_with(docs: dict):
    r = HybridRetriever(HashEmbedder(), InMemoryVectorStore())
    for did, text in docs.items():
        r.add(HashEmbedder().embed([text]), [text], [{"chunk_id": did + "#0", "doc_id": did}])
    return r


def test_hybrid_selects_correct_doc_among_three():
    docs = {
        "doc1": "Photosynthesis converts sunlight into chemical energy stored in plants.",
        "doc2": "Thermodynamics studies heat and energy transfer between systems.",
        "doc3": "Relativity describes space-time curvature near massive objects.",
    }
    r = _retriever_with(docs)
    hits = r.search("thermodynamics heat energy", k=3)
    assert len(hits) >= 1
    assert hits[0].doc_id == "doc2"


def test_bm25_two_doc_edge_no_reversal():
    # 仅 2 篇文档、目标词只在其中一篇，BM25 不应排序反转
    docs = {
        "a": "alpha beta gamma quantum",
        "b": "delta epsilon omega network",
    }
    r = _retriever_with(docs)
    hits = r.search("alpha", k=2)
    assert hits[0].doc_id == "a"


def test_empty_retriever():
    r = HybridRetriever(HashEmbedder(), InMemoryVectorStore())
    assert r.search("anything", k=5) == []
