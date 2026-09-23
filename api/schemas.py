"""WorldAI Nexus - API 层: 请求/响应模型。

作者: 晨星
"""
from __future__ import annotations

from pydantic import BaseModel


class IngestRequest(BaseModel):
    text: str | None = None
    doc_id: str = "mem"
    file: str | None = None


class ChatRequest(BaseModel):
    query: str
    k: int = 5
    use_rag: bool = True


class SearchRequest(BaseModel):
    query: str
    k: int = 5


class ChatSource(BaseModel):
    chunk_id: str
    doc_id: str
    score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    model: str
    sources: list[ChatSource]
    tool_calls: list[dict]


class SearchHitItem(BaseModel):
    chunk_id: str
    doc_id: str
    score: float
    text: str


class SearchResponse(BaseModel):
    hits: list[SearchHitItem]


class IngestResponse(BaseModel):
    chunks: int


class HealthResponse(BaseModel):
    status: str
    llm: str
    embedder: str
    vectorstore: str
