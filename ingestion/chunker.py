"""WorldAI Nexus - Ingestion 模块: 递归字符切分器。

按句末标点切分，按 chunk_size 打包，相邻块保留 overlap 重叠，保证上下文连续。

作者: 晨星
"""
from __future__ import annotations

import re

_SENT_RE = re.compile(r"(?<=[。.!?！？\n])")


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """将长文本切分为不超过 chunk_size 的片段，片段间保留 overlap 字符重叠。"""
    text = text.strip()
    if not text:
        return []
    sentences = [s for s in _SENT_RE.split(text) if s.strip()]
    if not sentences:
        sentences = [text]
    chunks: list[str] = []
    cur = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if cur and len(cur) + len(s) > chunk_size:
            chunks.append(cur.strip())
            cur = cur[-overlap:] + s
        else:
            cur += s
    if cur.strip():
        chunks.append(cur.strip())
    return chunks
