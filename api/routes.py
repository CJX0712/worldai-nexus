"""WorldAI Nexus - API 层: 路由 (仅装配，零业务)。

所有业务逻辑委托给 Container 注入的 agent / retriever / tools。
注意: 路由函数不标注返回类型，规避 FastAPI "Invalid args for response field" 联合类型坑。

作者: 晨星
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ChatRequest,
    ChatResponse,
    ChatSource,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
    SearchHitItem,
)


def make_router(container) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    def health():
        return HealthResponse(
            status="ok",
            llm=container.llm.name,
            embedder=container.embedder.__class__.__name__,
            vectorstore=container.retriever.vectorstore.__class__.__name__,
        )

    @router.post("/ingest", response_model=IngestResponse)
    def ingest(req: IngestRequest):
        if req.file:
            chunks = container.ingest_file(req.file)
        elif req.text is not None:
            chunks = container.ingest_text(req.text, req.doc_id)
        else:
            raise HTTPException(status_code=400, detail="provide text or file")
        return IngestResponse(chunks=len(chunks))

    @router.post("/chat", response_model=ChatResponse)
    def chat(req: ChatRequest):
        result = container.agent.run(req.query, k=req.k)
        return ChatResponse(
            answer=result.answer,
            model=result.model,
            sources=[
                ChatSource(
                    chunk_id=s.chunk_id,
                    doc_id=s.doc_id,
                    score=round(s.score, 4),
                    text=s.text[:200],
                )
                for s in result.sources
            ],
            tool_calls=[{"name": t.name, "result": t.result} for t in result.tool_calls],
        )

    @router.post("/search", response_model=SearchResponse)
    def search(req: SearchRequest):
        hits = container.retriever.search(req.query, req.k)
        return SearchResponse(
            hits=[
                SearchHitItem(
                    chunk_id=h.chunk_id,
                    doc_id=h.doc_id,
                    score=round(h.score, 4),
                    text=h.text[:200],
                )
                for h in hits
            ]
        )

    @router.get("/tools")
    def tools():
        return {"tools": container.tools.list()}

    @router.get("/eval")
    def eval_endpoint():
        from eval import run_eval

        passed, total = run_eval(container)
        return {"passed": passed, "total": total, "ok": passed == total}

    return router
