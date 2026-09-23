"""WorldAI Nexus - Embeddings 模块: Mock 离线实现。

基于字符级哈希 + 中英文 bigram 的确定性向量。相似文本共享 token，余弦相似度更高。
无需任何模型权重，保证离线可验证。

作者: 晨星
"""
from __future__ import annotations

import hashlib
import math
import re

_ASCII_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokens(text: str) -> list[str]:
    toks: list[str] = [w.lower() for w in _ASCII_RE.findall(text)]
    cjk = [c for c in text if "一" <= c <= "鿿"]
    toks.extend(cjk)
    for i in range(len(cjk) - 1):
        toks.append(cjk[i] + cjk[i + 1])
    return toks


class HashEmbedder:
    """确定性哈希嵌入器 (离线)。"""
    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _tokens(text):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) & 1 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
