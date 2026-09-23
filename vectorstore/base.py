"""WorldAI Nexus - VectorStore 模块: 公共工具。

作者: 晨星
"""
from __future__ import annotations

import math


def cosine(a: list[float], b: list[float]) -> float:
    """余弦相似度。空向量返回 0.0。"""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
