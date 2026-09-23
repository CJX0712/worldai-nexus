"""WorldAI Nexus - Ingestion 模块: 入库流水线。

职责单一: 文档 -> 切分 -> 嵌入 -> 写入向量库。依赖 Embedder 与 VectorStore 两个 Protocol，
不关心具体实现，可在测试中以 Mock 注入。

作者: 晨星
"""
from __future__ import annotations

from core.types import Chunk, Document


class IngestionPipeline:
    def __init__(self, embedder, vectorstore, chunk_size: int = 400, overlap: int = 80) -> None:
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.chunk_size = chunk_size
        self.overlap = overlap

    def ingest_document(self, doc: Document) -> list[Chunk]:
        from ingestion.chunker import chunk_text

        texts = chunk_text(doc.text, self.chunk_size, self.overlap)
        if not texts:
            return []
        chunks = [
            Chunk(
                chunk_id=f"{doc.doc_id}#{i}",
                doc_id=doc.doc_id,
                text=t,
                index=i,
                meta={"source": doc.source},
            )
            for i, t in enumerate(texts)
        ]
        vectors = self.embedder.embed([c.text for c in chunks])
        metas = [
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "source": c.meta.get("source", ""),
                "index": c.index,
            }
            for c in chunks
        ]
        self.vectorstore.add(vectors, [c.text for c in chunks], metas)
        return chunks

    def ingest_file(self, path: str) -> list[Chunk]:
        from ingestion.loaders import load_file

        return self.ingest_document(load_file(path))

    def ingest_text(self, text: str, doc_id: str = "mem") -> list[Chunk]:
        return self.ingest_document(Document(doc_id=doc_id, text=text, source="inline"))
