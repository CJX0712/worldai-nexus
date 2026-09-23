"""离线单元测试: 文档切分与入库流水线。"""
from embeddings.mock import HashEmbedder
from ingestion.chunker import chunk_text
from ingestion.pipeline import IngestionPipeline
from vectorstore.memory import InMemoryVectorStore


def test_chunker_respects_size_and_overlap():
    text = ("句子一内容。",) * 200  # 远超 chunk_size
    chunks = chunk_text("".join(text), chunk_size=200, overlap=40)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 200 + 40  # 含 overlap 不外溢过多


def test_pipeline_short_doc_single_chunk():
    pipe = IngestionPipeline(HashEmbedder(), InMemoryVectorStore())
    chunks = pipe.ingest_text("短文档内容。", doc_id="d1")
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "d1#0"


def test_pipeline_long_doc_multiple_chunks():
    pipe = IngestionPipeline(HashEmbedder(), InMemoryVectorStore())
    text = "世界人工智能大会展示了最新大模型能力。" * 50
    chunks = pipe.ingest_text(text, doc_id="d2")
    assert len(chunks) > 1
    # 入库后可被检索到
    hits = pipe.vectorstore.search(HashEmbedder().embed(["世界人工智能大会"])[0], k=1)
    assert len(hits) >= 1
