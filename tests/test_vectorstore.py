"""离线单元测试: 向量存储 (InMemoryVectorStore)。"""
from core.types import SearchHit
from vectorstore.base import cosine
from vectorstore.memory import InMemoryVectorStore


def test_add_and_search_returns_top():
    vs = InMemoryVectorStore()
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    c = [0.0, 0.0, 1.0]
    vs.add([a, b, c], ["a", "b", "c"], [{"chunk_id": "a"}, {"chunk_id": "b"}, {"chunk_id": "c"}])
    hits = vs.search([0.9, 0.1, 0.0], k=2)
    assert len(hits) == 2
    assert hits[0].chunk_id == "a"
    assert isinstance(hits[0], SearchHit)


def test_empty_store():
    vs = InMemoryVectorStore()
    assert vs.search([1.0], k=5) == []


def test_cosine_helper():
    assert abs(cosine([1.0, 0.0], [1.0, 0.0]) - 1.0) < 1e-9
    assert abs(cosine([1.0, 0.0], [0.0, 1.0])) < 1e-9
    assert cosine([], []) == 0.0
