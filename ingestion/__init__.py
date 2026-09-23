"""WorldAI Nexus - Ingestion 模块。

作者: 晨星
"""
from ingestion.chunker import chunk_text
from ingestion.loaders import load_file, load_pdf, load_text
from ingestion.pipeline import IngestionPipeline

__all__ = ["IngestionPipeline", "load_file", "load_text", "load_pdf", "chunk_text"]
__author__ = "晨星"
