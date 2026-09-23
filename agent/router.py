"""WorldAI Nexus - Agent 模块: 确定性路由。

对输入做轻量前置路由: 命中纯 ASCII 算术表达式则交由 calculator 工具，
避免小模型重算出错 (0.5B 小模型 ReAct 直接算术不可靠的已知坑)。其余走 RAG + LLM。

作者: 晨星
"""
from __future__ import annotations

import re

_ARITH_RE = re.compile(r"^[\d\s\.\+\-\*\/\(\)\%\^]+$")


def is_arithmetic(query: str) -> bool:
    """判断输入是否为可安全计算的纯算术表达式。"""
    q = (query or "").strip()
    if not q:
        return False
    if not re.search(r"\d", q):
        return False
    if not re.search(r"[\+\-\*\/\%\^]", q):
        return False
    return bool(_ARITH_RE.match(q))
