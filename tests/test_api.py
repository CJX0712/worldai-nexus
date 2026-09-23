"""离线集成测试: HTTP API (FastAPI TestClient, mock 后端)。"""
from fastapi.testclient import TestClient

from api.app import create_app
from core.config import AppConfig


def _client():
    cfg = AppConfig(llm_provider="mock", embedder="mock", vectorstore="memory")
    return TestClient(create_app(cfg))


def test_health():
    r = _client().get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ingest_and_chat():
    c = _client()
    r = c.post("/ingest", json={"text": "WorldAI Nexus 是晨星打造的模块化 AI 系统。", "doc_id": "t"})
    assert r.status_code == 200
    assert r.json()["chunks"] >= 1
    r2 = c.post("/chat", json={"query": "WorldAI Nexus 是什么？", "k": 3})
    assert r2.status_code == 200
    body = r2.json()
    assert body["model"] == "mock"
    assert ("晨星" in body["answer"]) or len(body["sources"]) >= 1


def test_search():
    c = _client()
    c.post("/ingest", json={"text": "量子计算利用叠加与纠缠实现并行计算。", "doc_id": "q"})
    r = c.post("/search", json={"query": "量子计算", "k": 2})
    assert r.status_code == 200
    assert len(r.json()["hits"]) >= 1


def test_eval():
    r = _client().get("/eval")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_ingest_missing_body():
    r = _client().post("/ingest", json={})
    assert r.status_code == 400
