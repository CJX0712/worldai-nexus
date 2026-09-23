"""WorldAI Nexus - Ingestion 模块: 文档加载器。

支持 .txt/.md/.text 与 .pdf。PDF 使用 pypdf (按需懒加载)，避免无谓依赖。

作者: 晨星
"""
from __future__ import annotations

import os

from core.errors import IngestionError
from core.types import Document


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise IngestionError("未安装 pypdf，请执行 pip install pypdf") from exc
    reader = PdfReader(path)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)


def load_file(path: str) -> Document:
    if not os.path.isfile(path):
        raise IngestionError(f"文件不存在: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".text"):
        text = load_text(path)
    elif ext == ".pdf":
        text = load_pdf(path)
    else:
        raise IngestionError(f"不支持的文件类型: {ext}")
    return Document(doc_id=os.path.basename(path), text=text, source=path)
